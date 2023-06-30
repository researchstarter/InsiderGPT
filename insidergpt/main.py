import loguru
import sys
import argparse

from insidergpt.utils.pentest_gpt import insiderGPT

logger = loguru.logger


def main():

    parser = argparse.ArgumentParser(description="InsiderGPT")
    parser.add_argument("--reasoning_model", type=str, default="gpt-4")
    parser.add_argument("--useAPI", action="store_true", default=False)
    parser.add_argument(
        "--baseUrl",
        type=str,
        default="https://api.openai.com/v1",
        help=,"OpenAI API uchun asosiy URL: https://api.openai.com/v1"
    )
    args = parser.parse_args()

    insiderGPTHandler = insiderGPT(
        reasoning_model=args.reasoning_model, useAPI=args.useAPI, baseUrl=args.baseUrl
    )

  
    insiderGPTHandler.main()


if __name__ == "__main__":
    main()
