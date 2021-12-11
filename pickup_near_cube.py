import cozmo
import datetime
from PIL import Image, ImageDraw, ImageFont
import time
import math

def pickup_and_put_on_ground(robot: cozmo.robot.Robot):
    lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=60)
    lookaround.stop()

    if len(cubes) > 0:
        target = cubes[0]
        robot.pickup_object(target, num_retries=3).wait_for_completed()
        robot.place_object_on_ground_here(target, num_retries=3).wait_for_completed()
    else:
        print("No cubes found")

def go_to_charger(robot: cozmo.robot.Robot):
    charger = None

    if robot.world.charger:
        if robot.world.charger.pose.is_comparable(robot.pose):
            charger = robot.world.charger
        else:
            pass

    if not charger:
        lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try:
            charger = robot.world.wait_for_observed_charger(timeout=30)
        except:
            print("Didnt see the charger")
        finally:
            lookaround.stop()

    if charger:
        robot.go_to_object(charger, cozmo.util.distance_mm(65.0)).wait_for_completed()

def make_clock_image(current_time):
    '''Make a PIL.Image with the current time displayed on it

    Args:
        text_to_draw (:class:`datetime.time`): the time to display

    Returns:
        :class:(`PIL.Image.Image`): a PIL image with the time displayed on it
    '''

    time_text = time.strftime("%I:%M:%S %p")

    # make a blank image for the text, initialized to opaque black
    clock_image = Image.new('RGBA', cozmo.oled_face.dimensions(), (0, 0, 0, 255))

    # get a drawing context
    dc = ImageDraw.Draw(clock_image)

    # calculate position of clock elements
    text_height = 9
    screen_width, screen_height = cozmo.oled_face.dimensions()
    analog_width = screen_width
    analog_height = screen_height - text_height
    cen_x = analog_width * 0.5
    cen_y = analog_height * 0.5

    # calculate size of clock hands
    sec_hand_length = (analog_width if (analog_width < analog_height) else analog_height) * 0.5
    min_hand_length = 0.85 * sec_hand_length
    hour_hand_length = 0.7 * sec_hand_length

    # calculate rotation for each hand
    sec_ratio = current_time.second / 60.0
    min_ratio = (current_time.minute + sec_ratio) / 60.0
    hour_ratio = (current_time.hour + min_ratio) / 12.0

    # draw the clock hands
    draw_clock_hand(dc, cen_x, cen_y, hour_ratio, hour_hand_length)
    draw_clock_hand(dc, cen_x, cen_y, min_ratio, min_hand_length)
    draw_clock_hand(dc, cen_x, cen_y, sec_ratio, sec_hand_length)

    # draw the digital time_text at the bottom
    x = 32
    y = screen_height - text_height
    dc.text((x, y), time_text, fill=(255, 255, 255, 255), font=None)

    return clock_image

def draw_clock_hand(dc, cen_x, cen_y, circle_ratio, hand_length):
    '''Draw a single clock hand (hours, minutes or seconds)

    Args:
        dc: (:class:`PIL.ImageDraw.ImageDraw`): drawing context to use
        cen_x (float): x coordinate of center of hand
        cen_y (float): y coordinate of center of hand
        circle_ratio (float): ratio (from 0.0 to 1.0) that hand has travelled
        hand_length (float): the length of the hand
    '''

    hand_angle = circle_ratio * math.pi * 2.0
    vec_x = hand_length * math.sin(hand_angle)
    vec_y = -hand_length * math.cos(hand_angle)

    # x_scalar doubles the x size to compensate for the interlacing
    # in y that would otherwise make the screen appear 2x tall
    x_scalar = 2.0

    # pointy end of hand
    hand_end_x = int(cen_x + (x_scalar * vec_x))
    hand_end_y = int(cen_y + vec_y)

    # 2 points, perpendicular to the direction of the hand,
    # to give a triangle with some width
    hand_width_ratio = 0.1
    hand_end_x2 = int(cen_x - ((x_scalar * vec_y) * hand_width_ratio))
    hand_end_y2 = int(cen_y + (vec_x * hand_width_ratio))
    hand_end_x3 = int(cen_x + ((x_scalar * vec_y) * hand_width_ratio))
    hand_end_y3 = int(cen_y - (vec_x * hand_width_ratio))

    dc.polygon([(hand_end_x, hand_end_y), (hand_end_x2, hand_end_y2),
                (hand_end_x3, hand_end_y3)], fill=(255, 255, 255, 255))

def draw_clock(robot: cozmo.robot.Robot):
    current_time = datetime.datetime.now().time()

    clock_image = make_clock_image(current_time)
    oled_face_data = cozmo.oled_face.convert_image_to_screen_data(clock_image)

    robot.display_oled_face_image(oled_face_data, 1000.0)

_clock_font = None
