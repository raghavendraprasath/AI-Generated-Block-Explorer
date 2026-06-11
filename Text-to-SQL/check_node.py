#!/usr/bin/env python3
"""Verify bitcoind RPC is reachable (Homework 3 §1)."""

import argparse
import json
import sys

from ingest import bitcoin_rpc

DEFAULT_RPC_URL = "http://127.0.0.1:8332"
DEFAULT_RPC_USER = "test"
DEFAULT_RPC_PASSWORD = "test"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check bitcoind RPC status")
    parser.add_argument("--rpc-url", default=DEFAULT_RPC_URL)
    parser.add_argument("--rpc-user", default=DEFAULT_RPC_USER)
    parser.add_argument("--rpc-password", default=DEFAULT_RPC_PASSWORD)
    parser.add_argument("--verbosity", type=int, default=1, help="getblock verbosity (1=summary)")
    args = parser.parse_args()

    try:
        count = bitcoin_rpc(args.rpc_url, args.rpc_user, args.rpc_password, "getblockcount")
        info = bitcoin_rpc(args.rpc_url, args.rpc_user, args.rpc_password, "getblockchaininfo")
        tip_hash = bitcoin_rpc(args.rpc_url, args.rpc_user, args.rpc_password, "getblockhash", [count])
        tip_block = bitcoin_rpc(
            args.rpc_url, args.rpc_user, args.rpc_password, "getblock", [tip_hash, args.verbosity]
        )
    except Exception as exc:
        print(f"ERROR: RPC failed — is bitcoind running? {exc}", file=sys.stderr)
        return 1

    print("getblockcount:", count)
    print("getblockchaininfo:")
    print(json.dumps(info, indent=2))
    print(f"\ngetblockhash({count}):", tip_hash)
    print(f"getblock({tip_hash!r}, {args.verbosity}) — last downloaded block:")
    print(json.dumps(tip_block, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
