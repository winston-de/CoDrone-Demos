import math

from codrone_edu.drone import *
import play
from random import randint

sc = play.screen

drone = Drone()
drone.pair()

play.set_backdrop("light-blue")
img = play.new_image("drone.png", 0, 0, 25)
score_text = play.new_text("", 0, sc.top - 15, font_size=30)

joystick_compensation_x = 0.075
joystick_compensation_y = 0.0125
x_decel = 0.25  # x deceleration rate
y_decel = 0.05  # y deceleration rate

game_over = False


def reset_game():
    """Resets score, drone position, etc"""
    img.throttle = 50
    img.score = 0
    img.delta_x = 0
    img.delta_y = 0
    img.x = 0
    img.y = 0
    score_text.words = "Avoid the clouds!"
    drone.set_controller_LED(0, 0, 128, 255)


reset_game()


@play.repeat_forever
def update_controls():
    global game_over

    if game_over:
        if drone.r1_pressed() or drone.l1_pressed():
            # reset game when l1 or r1 are pressed
            game_over = False
            reset_game()
        else:
            return

    data = drone.get_joystick_data()
    x_data = data[5] * joystick_compensation_x
    # if no x joystick input, do deceleration
    if x_data == 0:
        if abs(img.delta_x) < x_decel*2:
            # if slow enough, set to zero to avoid the velocity switching signs
            img.delta_x = 0
        else:
            img.delta_x += x_decel if img.delta_x < 0 else -x_decel
    else:
        img.delta_x = x_data

    img.angle = img.delta_x * -2  # tilt the drone based on x-velocity to make it more realistic

    y_data = data[2] * joystick_compensation_y
    if abs(y_data) <= 0.25:  # ignore very small or zero inputs
        if abs(img.delta_y) < y_decel*2:
            # if the y delta is slow enough, just stop it.
            # This prevents the velocity from switching signs
            img.delta_y = 0
        else:
            # decelerate the y velocity to make it feel more realistic
            img.delta_y += y_decel if img.delta_y < 0 else -y_decel
    else:
        # if there is joystick input, set the throttle delta to the input
        img.delta_y = y_data

    # set the x, clamp the x, so the drone can't fly off screen
    img.x = clamp(sc.left, sc.right, img.x + img.delta_x)

    # update throttle (between 0 and 100)
    img.throttle = clamp(0, 100, img.throttle + img.delta_y)
    # convert throttle to screen position
    img.y = sc.bottom + sc.height * img.throttle/100


clouds = []
wait_time = 3
cloud_speed = 4


@play.repeat_forever
async def create_clouds():
    global wait_time, cloud_speed

    if game_over:
        return

    y = randint(int(sc.bottom), int(sc.top - 15))  # random y between bottom and top of screen minus padding
    start_left = randint(0, 1) == 1
    start_x = sc.left if start_left else sc.right

    size = randint(75, 100)
    cloud = play.new_image("cloud.png", start_x, y, size)
    cloud.speed = cloud_speed if start_left else -cloud_speed  # if starting on left, move left, otherwise move right
    clouds.append(cloud)

    if wait_time > 3:
        # after 3 seconds, start increasing the difficulty
        wait_time *= 0.75
        cloud_speed = math.ceil(cloud_speed * 1.25)

    await play.timer(wait_time)


@play.repeat_forever
async def update_clouds():
    global game_over, sound

    if game_over:
        return

    cloud: play.Sprite  # tell python clouds are sprites, allows for autocomplete

    for cloud in clouds:
        # helper function to remove this cloud
        def remove_cloud():
            cloud.remove()
            clouds.remove(cloud)

        cloud.x += cloud.speed
        # PyCharm will complain, ignore it because we add a speed instance var to every cloud instance
        if ((cloud.speed < 0 and cloud.x < sc.left - cloud.width) or
                (cloud.speed > 0 and cloud.x > sc.right + cloud.width)):
            # if going left, check if colliding with left border
            # if going right, check if colliding with right border

            img.score += 1
            score_text.words = f"Score: {img.score}"
            sound = 0  # play happy tune
            remove_cloud()

        if cloud.is_touching(img):
            game_over = True
            score_text.words = "You lost :(     (Press R1 or L1 to try again)"
            drone.set_controller_LED(255, 0, 0, 255)  # set controller to red
            sound = 1  # play womp-womp
            remove_cloud()

# calling the drone buzzer function will block the current thread, so we use this workaround to avoid freezing the game
# or using the threadpool.
# set the sound variable to the desired tune to be played, and replit will always run this function parallel to the
# other functions in the game. Note: this will not work well (last tune will be skipped) if a new tune is set to be
# played before the current one finishes.

sound = -1


@play.repeat_forever
async def play_sound():
    global sound
    if sound == -1:  # no sound, exit
        return

    elif sound == 0:  # ding for score change
        drone.sendVibrator(150, 150, 600)
        drone.start_controller_buzzer(Note.C6)
        await play.timer(0.15)
        drone.start_controller_buzzer(Note.E6)
        await play.timer(0.15)
        drone.stop_controller_buzzer()

    elif sound == 1:  # womp womp
        drone.sendVibrator(100, 0, 500)
        drone.start_controller_buzzer(Note.G3)
        await play.timer(0.15)
        drone.start_controller_buzzer(Note.FS3)
        await play.timer(0.15)
        drone.stop_controller_buzzer()

    sound = -1  # reset sound to be played


def clamp(_min, _max, _input):
    """Clamps the input to be within the given range"""
    return max(_min, min(_max, _input))


play.start_program()
