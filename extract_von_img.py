#!/usr/bin/env python3
"""
extract_von_img.py - Stage 1: Extract files and audio from a VON ISO 9660 image.

Reads an ISO 9660 CD-ROM image (e.g. von.img) and:
  1. Extracts all files from the filesystem into a data/ directory.
  2. Converts raw 8-bit unsigned PCM audio blobs to playable WAV files.

Usage:
  python3 extract_von_img.py von.img [--output OUTDIR] [--rate SAMPLE_RATE]
"""

import struct
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


class Iso9660Reader:
    """Reads files from an ISO 9660 filesystem image."""

    def __init__(self, path):
        self._f = open(path, "rb")
        self._block_size = 2048
        self._pvd_offset = 0x8000  # LBA 16
        self._read_pvd()

    def _read_pvd(self):
        self._f.seek(self._pvd_offset)
        pvd = self._f.read(2048)
        if pvd[0] != 1:
            raise ValueError("Primary Volume Descriptor not found at LBA 16")
        if pvd[1:6] != b"CD001":
            raise ValueError("Not a valid ISO 9660 image")
        self._block_size = struct.unpack_from("<H", pvd, 0x80)[0]
        self.volume_id = pvd[40:72].decode("ascii").strip()
        self.system_id = pvd[8:40].decode("ascii").strip()
        # Application identifier at PVD offset 574 (0x23E), 128 bytes
        self.app_id = pvd[0x23E : 0x23E + 128].decode("ascii", errors="replace").strip()
        # Root directory record at offset 156 in PVD
        root_rec = pvd[0x9C:]
        self._root_lba = struct.unpack_from("<I", root_rec, 2)[0]
        self._root_size = struct.unpack_from("<I", root_rec, 10)[0]

    def _read_extent(self, lba, size):
        self._f.seek(lba * self._block_size)
        return self._f.read(size)

    def _parse_dir(self, lba, size):
        """Parse directory entries, returning list of (name, lba, size, is_dir)."""
        data = self._read_extent(lba, size)
        entries = []
        pos = 0
        while pos < len(data):
            rec_len = data[pos]
            if rec_len == 0:
                pos += 1
                continue
            if pos + rec_len > len(data):
                break

            flags = data[pos + 25]
            name_len = data[pos + 32]
            name = data[pos + 33 : pos + 33 + name_len].decode("ascii", errors="replace")

            # Skip "." and ".." entries (name_len == 1 and name == '\x00' or '\x01')
            if name_len == 1 and name in ("\x00", "\x01"):
                pos += rec_len
                continue

            extent = struct.unpack_from("<I", data, pos + 2)[0]
            data_len = struct.unpack_from("<I", data, pos + 10)[0]
            is_dir = bool(flags & 2)

            entries.append((name, extent, data_len, is_dir))
            pos += rec_len

        return entries

    def extract_all(self, outdir):
        """Extract all files from the ISO to outdir, preserving directory structure."""
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        def extract_dir(lba, size, current_path):
            current_path.mkdir(parents=True, exist_ok=True)
            for name, extent, data_len, is_dir in self._parse_dir(lba, size):
                dest = current_path / name
                if is_dir:
                    extract_dir(extent, data_len, dest)
                else:
                    data = self._read_extent(extent, data_len)
                    dest.write_bytes(data)

        extract_dir(self._root_lba, self._root_size, outdir)

    def get_file_list(self):
        """Return a flat list of (relative_path, lba, size, is_dir)."""

        def walk(lba, size, prefix):
            results = []
            for name, extent, data_len, is_dir in self._parse_dir(lba, size):
                path = f"{prefix}/{name}" if prefix else name
                results.append((path, extent, data_len, is_dir))
                if is_dir:
                    results.extend(walk(extent, data_len, path))
            return results

        return walk(self._root_lba, self._root_size, "")

    def close(self):
        self._f.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def raw_pcm_to_wav(pcm_data, outpath, sample_rate=22050, channels=1, bits=8):
    """Convert raw unsigned 8-bit PCM data to a WAV file with RIFF header."""
    byte_rate = sample_rate * channels * (bits // 8)
    block_align = channels * (bits // 8)
    data_size = len(pcm_data)

    riff_size = 36 + data_size
    fmt_size = 16
    audio_format = 1  # PCM

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        riff_size,
        b"WAVE",
        b"fmt ",
        fmt_size,
        audio_format,
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits,
        b"data",
        data_size,
    )

    with open(outpath, "wb") as f:
        f.write(header)
        f.write(pcm_data)


def main():
    parser = argparse.ArgumentParser(
        description="Extract files and audio from a VON ISO 9660 image."
    )
    parser.add_argument("image", help="Path to .img or .iso file")
    parser.add_argument(
        "--output", "-o", default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=22050,
        help="Sample rate for raw PCM audio conversion (default: 22050 Hz)",
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Skip audio conversion, only extract files",
    )
    args = parser.parse_args()

    outdir = Path(args.output)

    with Iso9660Reader(args.image) as iso:
        print(f"ISO 9660 image: {args.image}")
        print(f"  Volume ID : {iso.volume_id}")
        print(f"  System ID : {iso.system_id}")
        print(f"  Application: {iso.app_id}")
        print(f"  Block size: {iso._block_size}")

        # Stage 1a: Extract all files
        data_dir = outdir / "data"
        print(f"\nExtracting all files to {data_dir}/ ...")
        iso.extract_all(data_dir)

        file_count = sum(1 for _ in data_dir.rglob("*") if _.is_file())
        dir_count = sum(1 for _ in data_dir.rglob("*") if _.is_dir())
        print(f"  Extracted {file_count} files in {dir_count} directories.")

        if args.no_audio:
            print("\nSkipping audio conversion (--no-audio).")
            return

        # Stage 1b: Convert raw audio blobs to WAV
        audio_dir = outdir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        audio_patterns = [
            # (glob_pattern, description)
            ("SND_*.BIN", "sound effect / voice clip"),
            ("ESCR*.BIN", "title / attract mode audio"),
        ]

        print(f"\nConverting raw audio to WAV in {audio_dir}/ ...")
        print(f"  Sample rate: {args.rate} Hz, 8-bit unsigned, mono")

        converted = 0
        for pattern, desc in audio_patterns:
            for fpath in sorted(data_dir.glob(f"**/{pattern}")):
                rel = fpath.relative_to(data_dir)
                wav_name = fpath.with_suffix(".wav").name
                wav_path = audio_dir / wav_name

                pcm = fpath.read_bytes()
                raw_pcm_to_wav(pcm, wav_path, sample_rate=args.rate)

                duration = len(pcm) / args.rate
                print(f"  {fpath.name:20s} -> {wav_name:20s}  "
                      f"({len(pcm):>8d} bytes, {duration:.2f}s, {desc})")
                converted += 1

        if converted:
            print(f"\n  Converted {converted} audio file(s).")
        else:
            print("\n  No raw audio files found.")

        # Also note any standard AVI files (already playable)
        avi_files = sorted(data_dir.rglob("*.AVI"))
        if avi_files:
            print(f"\nStandard AVI files (already playable):")
            for avi in avi_files:
                print(f"  {avi.relative_to(data_dir)}")


if __name__ == "__main__":
    main()
