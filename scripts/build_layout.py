#!/usr/bin/env python3
"""Generate a Steam Input layout from explicit keyboard/mouse bindings."""
from pathlib import Path
import vdf


def press(*bindings, soft=False, repeat=False):
    action = {'bindings': vdf.VDFDict([('binding', b) for b in bindings])}
    if repeat:
        action['settings'] = {'hold_repeats': '1', 'repeat_rate': '50', 'interruptable': '0'}
    return {'activators': {'Soft_Press' if soft else 'Full_Press': action}}


def keys(*names):
    return press(*(f'key_press {name}' for name in names))


def layout():
    groups = [
        ('0', 'four_buttons', 'button_diamond', {
            'button_a': keys('RETURN'), 'button_b': keys('ESCAPE'),
            'button_x': press('controller_action SHOW_KEYBOARD'), 'button_y': keys('TAB')}, {}),
        ('1', 'scrollwheel', 'left_trackpad', {
            'scroll_clockwise': press('mouse_wheel SCROLL_DOWN'),
            'scroll_counterclockwise': press('mouse_wheel SCROLL_UP'),
            'click': press('key_press LEFT_WINDOWS', 'key_press B', soft=True)},
            {'scroll_type': '2', 'scroll_angle': '160', 'scroll_friction': '1', 'haptic_intensity': '1'}),
        ('2', 'absolute_mouse', 'right_trackpad', {
            'click': press('mouse_button LEFT', soft=True)}, {}),
        ('3', 'dpad', 'joystick', {
            'dpad_north': keys('UP_ARROW'), 'dpad_south': keys('DOWN_ARROW'),
            'dpad_west': keys('LEFT_ARROW'), 'dpad_east': keys('RIGHT_ARROW'),
            'click': keys('LEFT_WINDOWS', 'T')}, {'requires_click': '0', 'deadzone_inner_radius': '7199'}),
        ('4', 'trigger', 'left_trigger', {'edge': press('mouse_button RIGHT')}, {}),
        ('5', 'trigger', 'right_trigger', {'edge': press('mouse_button LEFT')}, {}),
        ('6', 'joystick_mouse', 'right_joystick', {
            'click': keys('LEFT_WINDOWS', 'LEFT_SHIFT', 'RETURN')}, {'output_joystick': '2'}),
        ('7', 'switches', 'switch', {
            'button_escape': keys('LEFT_WINDOWS', 'LEFT_SHIFT', 'P'),
            'button_menu': keys('LEFT_WINDOWS', 'P'),
            'button_back_left_upper': keys('LEFT_WINDOWS', 'LEFT_SHIFT', 'LEFT_BRACKET'),
            'button_back_right_upper': keys('LEFT_WINDOWS', 'LEFT_SHIFT', 'RIGHT_BRACKET'),
            'button_back_left': keys('LEFT_WINDOWS', 'C'),
            'button_back_right': keys('LEFT_WINDOWS', 'V')}, {}),
        ('8', 'dpad', 'dpad', {
            'dpad_north': press('mouse_wheel SCROLL_UP', repeat=True),
            'dpad_south': press('mouse_wheel SCROLL_DOWN', repeat=True),
            'dpad_west': keys('LEFT_WINDOWS', 'LEFT_ALT', 'LEFT_ARROW'),
            'dpad_east': keys('LEFT_WINDOWS', 'LEFT_ALT', 'RIGHT_ARROW')}, {'requires_click': '0'}),
    ]
    mapping = vdf.VDFDict([
        ('version', '3'), ('revision', '1'), ('title', 'Deckystation - Herdr'),
        ('description', 'Mouse, scroll, terminal keys and Herdr shortcuts. L1+R1 reserved for dictation.'),
        ('controller_type', 'controller_neptune'), ('controller_caps', '23117823'),
        ('major_revision', '1'), ('minor_revision', '0'),
    ])
    sources = {}
    for identifier, mode, source, inputs, settings in groups:
        mapping['group'] = {'id': identifier, 'mode': mode, 'inputs': inputs, 'settings': settings}
        sources[identifier] = source + ' active'
    mapping['preset'] = {'id': '0', 'name': 'Default', 'group_source_bindings': sources}
    mapping['settings'] = {'left_trackpad_mode': '0', 'right_trackpad_mode': '0'}
    return vdf.VDFDict([('controller_mappings', mapping)])


if __name__ == '__main__':
    destination = Path(__file__).resolve().parents[1] / 'config/herdr-controller.vdf'
    destination.write_text(vdf.dumps(layout(), pretty=True))
    print(destination)
