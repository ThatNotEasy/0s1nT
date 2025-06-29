import argparse
import os
import logging
from modules.logging import setup_logging

def validate_file(path):
    """Validate that the input file exists"""
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File '{path}' does not exist")
    return path

def validate_json_output(path):
    """Validate that output path ends with .json"""
    if not path.lower().endswith('.json'):
        raise argparse.ArgumentTypeError("Output file must be in .json format")
    return path

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Social Media Account Checker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help="Username to check"
    )

    parser.add_argument(
        '-o', '--output',
        type=validate_json_output,
        required=False,
        help="Path to output file (must be .json format)"
    )

    # Optional arguments
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=3,
        help="Number of threads to use (1-32)"
    )

    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help="Increase verbosity level (use -v for INFO, -vv for DEBUG)"
    )

    args = parser.parse_args()
    
    # Configure logging based on verbosity
    logger = setup_logging("SOCMED")
    if args.verbose >= 2:
        logger.setLevel(logging.DEBUG)
    elif args.verbose == 1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)
    
    return args, logger