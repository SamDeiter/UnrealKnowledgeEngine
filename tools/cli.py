
import sys
import os
import argparse
from rich.console import Console

# Add current directory to sys.path to ensure modules can be imported
sys.path.append(os.getcwd())

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Unreal Knowledge Engine (UKE) CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # uke init
    parser_init = subparsers.add_parser("init", help="Initialize folder structure and context")

    # uke gate
    parser_gate = subparsers.add_parser("gate", help="Validate LOs and evidence")
    parser_gate.add_argument("--engine", help="Path to Unreal Engine root")
    parser_gate.add_argument("--no-capture", action="store_true", help="Skip capture validation")

    # uke capture
    parser_capture = subparsers.add_parser("capture", help="Run capture for an LO")
    parser_capture.add_argument("--engine", required=True, help="Path to Unreal Engine root")
    parser_capture.add_argument("--lo", required=True, help="Learning Object ID")

    # uke heal
    parser_heal = subparsers.add_parser("heal", help="Auto-heal cosmetic drift")
    parser_heal.add_argument("--engine", required=True, help="Path to Unreal Engine root")
    parser_heal.add_argument("--from-sha", required=True, help="Old commit SHA")
    parser_heal.add_argument("--to-sha", required=True, help="New commit SHA")

    # uke plan
    parser_plan = subparsers.add_parser("plan", help="Generate learning path")
    parser_plan.add_argument("--context", required=True, help="Path to context.json")

    # uke site
    parser_site = subparsers.add_parser("site", help="Generate static site")

    # uke serve
    parser_serve = subparsers.add_parser("serve", help="Serve static site locally")

    args = parser.parse_args()

    if args.command == "init":
        from tools.init_cmd import run_init
        run_init()
    elif args.command == "gate":
        from tools.gate.cmd import run_gate
        run_gate(args.engine, args.no_capture)
    elif args.command == "capture":
        from tools.capture.cmd import run_capture
        run_capture(args.engine, args.lo)
    elif args.command == "heal":
        from tools.freshness.cmd import run_heal
        run_heal(args.engine, args.from_sha, args.to_sha)
    elif args.command == "plan":
        from tools.path_planner.cmd import run_plan
        run_plan(args.context)
    elif args.command == "site":
        from tools.site_gen.cmd import run_site
        run_site()
    elif args.command == "serve":
        from tools.serve_cmd import run_serve
        run_serve()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
