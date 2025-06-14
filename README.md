# MagiskFakehttp

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/Droid-MAX/magisk-fakehttp/main.yml?branch=main)
![GitHub repo size](https://img.shields.io/github/repo-size/Droid-MAX/magisk-fakehttp)
![GitHub downloads](https://img.shields.io/github/downloads/Droid-MAX/magisk-fakehttp/total)

> [FakeHTTP](https://github.com/MikeWang000000/FakeHTTP) is a tool used to Obfuscate all your TCP connections into HTTP protocol.

> [MagiskFakehttp](README.md) lets you run fakehttp on boot with multiple root solutions

## Supported root solutions

[Magisk](https://github.com/topjohnwu/Magisk), [KernelSU](https://github.com/tiann/KernelSU) and [APatch](https://github.com/bmax121/APatch)

## Supported architectures

`arm32v7`, `arm64`, `i686`, `x86_64`

## Instructions

Install `MagiskFakehttp.zip` from [the releases](https://github.com/Droid-MAX/magisk-fakehttp/releases)

> :information_source: Do not use the Magisk modules repository, it is obsolete and no longer receives updates

## How fast are fakehttp updates?

Instant! This module is hooked up to the official FakeHTTP build process

## Issues?

Check out the [troubleshooting guide](TROUBLESHOOTING.md)

## Building yourself

```bash
uv sync
uv run python3 main.py
```

- Release ZIP will be under `/build`
- fakehttp downloads will be under `/downloads`
