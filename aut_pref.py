import argparse
import json
import time
from typing import Dict, Tuple

import pyautogui

pyautogui.sleep(3)

# Pause after each PyAutoGUI call to let the UI catch up.
COMMAND_PAUSE = 0.5
MOUSE_MOVE_DURATION = 0.5
DATE_DRAG_DISTANCE = 120

# Edit these coordinates to match your screen and app layout.

# All coordinates are in screen pixels.
COORDS: Dict[str, Tuple[int, int]] = {
    "data": (620, 170),
    "dados_do_bem": (242, 253),
    "n_da_nf": (236, 424),
    "data_da_nf": (445, 420),
    "quantidade": (640, 420),
    "valor": (445, 590),
    "categoria_button": (529, 361),
    "categoria_option": (464, 545),
    "fornecedor_search": (1214, 366),
    "fornecedor_field": (471, 317),
    "fornecedor_result": (570, 389),
    "conservacao_button": (447, 593),
    "departamento_button": (1162, 752),
    "departamento_option": (494, 380),
    "replicar": (401, 931),
    "salvar": (326, 931),
    "salvar_confirmacao": (658, 574),
    "salvar_ok": (755, 567),
    "novo_item": (318, 167),
    "nova_sessao": (335, 182),
}

FORNECEDOR_QUERY = "SM"


def load_coords(path: str) -> Dict[str, Tuple[int, int]]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
        print(data)
    return {k: (int(v[0]), int(v[1])) for k, v in data.items()}


def click_and_type(
    x: int,
    y: int,
    text: str,
    interval: float,
    *,
    double_click: bool = False,
    pre_delay: float = 0.0,
) -> None:
    if double_click:
        move_and_double_click(x, y)
    else:
        move_and_click(x, y)
    if pre_delay:
        time.sleep(pre_delay)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite(text, interval=interval)


def click_only(x: int, y: int) -> None:
    move_and_click(x, y)


def type_current_field(text: str, interval: float) -> None:
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite(text, interval=interval)


def require_coord(name: str) -> Tuple[int, int]:
    if name not in COORDS:
        raise SystemExit(
            f"Missing '{name}' in COORDS/coords JSON. "
            "Add it to click after salvar."
        )
    if COORDS[name] == (0, 0):
        raise SystemExit(
            f"Coordinate '{name}' is (0, 0). "
            "Update it with the correct screen position."
        )
    return COORDS[name]


def click_nova_sessao() -> None:
    click_only(*require_coord("nova_sessao"))


def click_salvar_confirmacao(delay: float) -> None:
    time.sleep(delay)
    click_only(*require_coord("salvar_confirmacao"))
    time.sleep(delay)
    click_only(*require_coord("salvar_ok"))


def click_novo_item(delay: float) -> None:
    time.sleep(delay)
    click_only(*require_coord("novo_item"))


def move_and_click(x: int, y: int) -> None:
    pyautogui.moveTo(x, y, duration=MOUSE_MOVE_DURATION)
    pyautogui.click()


def move_and_double_click(x: int, y: int) -> None:
    pyautogui.moveTo(x, y, duration=MOUSE_MOVE_DURATION)
    pyautogui.doubleClick()


def drag_select_left(x: int, y: int) -> None:
    pyautogui.moveTo(x, y, duration=MOUSE_MOVE_DURATION)
    pyautogui.mouseDown()
    pyautogui.moveTo(x - DATE_DRAG_DISTANCE, y, duration=MOUSE_MOVE_DURATION)
    pyautogui.mouseUp()


def drag_select_and_type_date(x: int, y: int, text: str, interval: float) -> None:
    move_and_click(x, y)
    drag_select_left(x, y)
    pyautogui.typewrite(text, interval=interval)


def select_dropdown(field: str) -> None:
    button_key = f"{field}_button"
    option_key = f"{field}_option"
    move_and_click(*COORDS[button_key])
    move_and_double_click(*COORDS[option_key])


def select_conservacao_with_keys() -> None:
    move_and_click(*COORDS["conservacao_button"])
    pyautogui.press("up", presses=1, interval=0.3)
    pyautogui.press("enter")


def select_fornecedor(interval: float) -> None:
    move_and_click(*COORDS["fornecedor_search"])
    move_and_click(*COORDS["fornecedor_field"])
    pyautogui.typewrite(FORNECEDOR_QUERY, interval=interval)
    pyautogui.press("enter")
    move_and_double_click(*COORDS["fornecedor_result"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Autofill cadastro de tombamento.")
    parser.add_argument("--data", required=True, help="DATA")
    parser.add_argument("--dados-do-bem", required=True, help="DADOS DO BEM")
    parser.add_argument("--n-da-nf", required=True, help="N DA NF")
    parser.add_argument("--data-da-nf", required=True, help="DATA DA NF")
    parser.add_argument("--quantidade", required=True, help="QUANTIDADE")
    parser.add_argument("--valor", required=True, help="VALOR")
    parser.add_argument("--coords", help="Path to JSON file with coordinates")
    parser.add_argument("--delay", type=float, default=0.3, help="Delay between actions")
    parser.add_argument("--type-interval", type=float, default=0.08, help="Typing interval")
    parser.add_argument("--replicar", action="store_true", help="Click Replicar")
    parser.add_argument("--salvar", action="store_true", help="Click Salvar")
    parser.add_argument("--nova-sessao", action="store_true", help="Click Nova Sessao")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.coords:
        global COORDS
        COORDS = load_coords(args.coords)

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = COMMAND_PAUSE
    time.sleep(args.delay)

    drag_select_and_type_date(*COORDS["data"], args.data, args.type_interval)
    click_and_type(
        *COORDS["dados_do_bem"],
        args.dados_do_bem,
        args.type_interval,
        double_click=True,
        pre_delay=0.2,
    )
    select_dropdown("categoria")
    click_and_type(*COORDS["n_da_nf"], args.n_da_nf, args.type_interval)
    drag_select_and_type_date(*COORDS["data_da_nf"], args.data_da_nf, args.type_interval)
    click_and_type(*COORDS["quantidade"], args.quantidade, args.type_interval)
    select_fornecedor(args.type_interval)
    select_conservacao_with_keys()
    type_current_field(args.valor, args.type_interval)
    select_dropdown("departamento")
    if args.replicar:
        click_only(*COORDS["replicar"])
    if args.salvar:
        click_only(*COORDS["salvar"])
        click_salvar_confirmacao(args.delay)
        if args.nova_sessao:
            click_novo_item(args.delay)
    if args.nova_sessao:
        click_nova_sessao()


if __name__ == "__main__":
    main()