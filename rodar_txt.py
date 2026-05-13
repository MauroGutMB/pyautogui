import argparse
import subprocess
import sys
from pathlib import Path


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in ("1", "true", "sim", "yes", "y"):
        return True
    if normalized in ("0", "false", "nao", "não", "no", "n", ""):
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def load_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig") as handle:
        lines = [line.rstrip("\n") for line in handle]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def trim_block(block: list[str]) -> list[str]:
    start = 0
    end = len(block)
    while start < end and block[start] == "":
        start += 1
    while end > start and block[end - 1] == "":
        end -= 1
    return block[start:end]


def split_blocks(lines: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.strip() == "---":
            if current:
                blocks.append(trim_block(current))
                current = []
            continue
        current.append(line)
    if current:
        blocks.append(trim_block(current))
    return [block for block in blocks if block]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read a TXT file and run aut_pref with its parameters. "
            "Use '---' to separate multiple blocks."
        )
    )
    parser.add_argument("--input", required=True, help="Path to TXT file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.is_file():
        raise SystemExit(f"Input file not found: {input_path}")

    lines = load_lines(input_path)
    blocks = split_blocks(lines)
    if not blocks:
        raise SystemExit("TXT is empty. Add at least one block with 6 lines.")

    script_path = Path(__file__).with_name("aut_pref.py")
    for index, block in enumerate(blocks, start=1):
        if len(block) < 6:
            raise SystemExit(
                "Each block must have at least 6 lines: data, dados_do_bem, "
                "n_da_nf, data_da_nf, quantidade, valor."
            )

        data, dados_do_bem, n_da_nf, data_da_nf, quantidade, valor = block[:6]
        replicar = parse_bool(block[6]) if len(block) >= 7 else False
        salvar = parse_bool(block[7]) if len(block) >= 8 else False

        cmd = [
            sys.executable,
            str(script_path),
            "--data",
            data,
            "--dados-do-bem",
            dados_do_bem,
            "--n-da-nf",
            n_da_nf,
            "--data-da-nf",
            data_da_nf,
            "--quantidade",
            quantidade,
            "--valor",
            valor,
        ]
        if replicar:
            cmd.append("--replicar")
        if salvar:
            cmd.append("--salvar")

        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
