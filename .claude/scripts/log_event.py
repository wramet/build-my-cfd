#!/usr/bin/env python3
"""
CLI wrapper for workflow logger.

Allows manual logging of agent invocations, proxy routing, and task events
from the command line or other scripts.

Usage:
    python log_event.py agent --name "content-expander" --model "deepseek" ...
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.workflow_logger import get_logger, log_phase, log_agent, log_proxy_routing, log_task_start, log_task_complete

def main():
    parser = argparse.ArgumentParser(description='Log workflow events manually')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Command: agent
    agent_parser = subparsers.add_parser('agent', help='Log agent invocation')
    agent_parser.add_argument('--name', required=True, help='Agent name')
    agent_parser.add_argument('--model', required=True, help='Model used')
    agent_parser.add_argument('--backend', required=True, help='Backend (proxy/direct)')
    agent_parser.add_argument('--task', required=True, help='Task description')

    # Command: proxy
    proxy_parser = subparsers.add_parser('proxy', help='Log proxy routing')
    proxy_parser.add_argument('--original', required=True, help='Original model')
    proxy_parser.add_argument('--mapped', required=True, help='Mapped model')
    proxy_parser.add_argument('--backend', required=True, help='Backend routed to')
    proxy_parser.add_argument('--reason', default="", help='Routing reason')

    # Command: phase
    phase_parser = subparsers.add_parser('phase', help='Log new phase')
    phase_parser.add_argument('--num', type=int, required=True, help='Phase number')
    phase_parser.add_argument('--name', required=True, help='Phase name')
    phase_parser.add_argument('--details', default=None, help='Phase details')

    # Command: task
    task_parser = subparsers.add_parser('task', help='Log task event')
    task_parser.add_argument('--name', required=True, help='Task name')
    task_parser.add_argument('--status', choices=['start', 'complete'], required=True, help='Task status')
    task_parser.add_argument('--result', default=None, help='Task result (for complete status)')

    args = parser.parse_args()
    
    # Initialize logger
    get_logger()

    if args.command == 'agent':
        log_agent(args.name, args.model, args.backend, args.task)
        print(f"Logged agent: {args.name}")

    elif args.command == 'proxy':
        log_proxy_routing(args.original, args.mapped, args.backend, args.reason)
        print(f"Logged proxy: {args.original} -> {args.mapped}")

    elif args.command == 'phase':
        log_phase(args.num, args.name, args.details)
        print(f"Logged phase: {args.name}")

    elif args.command == 'task':
        if args.status == 'start':
            log_task_start(args.name)
            print(f"Logged task start: {args.name}")
        else:
            log_task_complete(args.name, args.result)
            print(f"Logged task complete: {args.name}")

    else:
        parser.print_help()
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
