import math
import melodies
from helpers import *
from codrone_edu.drone import *

drone = Drone()
drone.pair()

songs = [melodies.take_on_me(), melodies.star_wars(), melodies.zelda(), melodies.game_of_thrones(),
         melodies.the_lion_sleeps_tonight(), melodies.never_gonna_give_you_up()]


def play_song(song: melodies.Song):
    mel = song.notes
    whole = song.whole_note
    drone.controller_clear_screen()
    draw_lines(drone, f"Now playing: {song.name}\nHold L2 to stop", 0, 0)
    for n in range(0, len(mel) - 1, 2):
        d = mel[n+1]

        if d < 0:
            # a negative duration denotes a dotted note
            # dotted notes are the original duration, plus the half that duration
            # eg -4 is a quarter note plus an eighth note
            d = -1 * (d + d*2)  # eq. 1/4 + 1/8, then remove the negative sign

        d = int(whole//d)  # convert fraction (eg 8 = 1/8 note) to a duration in ms

        drone.set_drone_LED(random.randint(100, 255), random.randint(100, 255),
                            random.randint(100, 255), 255)

        drone.drone_buzzer(mel[n], d)
        if drone.l2_pressed():
            debounce[3] = True
            break

    drone.stop_drone_buzzer()


current_sel = 0  # current selected song
page1offset = 3  # number of songs displayed on page 1
songs_per_page = 6  # songs displayed on every page but page 1
curr_page = 0
total_pages = math.ceil((len(songs) + page1offset) / songs_per_page)


def get_songs_in_range(start, stop):
    """Gets a string of songs in the library, within the specified range"""
    disp_str = ""
    for i in range(start, min(len(songs), stop)):
        disp_str += f"{i+1}: {songs[i].name}\n"

    return disp_str


def page_1():
    """Draws page one (read-as: includes instructions)"""
    disp_str = "L2 to quit, R2 to select\n"
    disp_str += "L1 -, R1 +\n"
    disp_str += get_songs_in_range(0, page1offset)
    return disp_str


def other_page():
    """Draws any page that isn't page one (read as: not page 1)"""
    start = page1offset + songs_per_page * (curr_page-1)
    return get_songs_in_range(start, start + songs_per_page)


def draw_display():
    disp_str = ""
    # treat page one different because it has instructions
    if curr_page == 0:
        disp_str += page_1()
    else:
        disp_str += other_page()
    drone.controller_clear_screen()
    draw_lines(drone, disp_str, 0, 0)

    # always draw page number and stuff at the bottom
    disp_str_2 = f"^ v pages ({curr_page+1}/{total_pages})\n"
    disp_str_2 += f"Current selection: {current_sel + 1}\n"
    disp_str_2 += f"    {songs[current_sel].name}"
    draw_lines(drone, disp_str_2, 0, 40)


# used to ensure actions are only taken once per button press
# set to true when pressed initially, set back to false once released
debounce = [False, False, False, False, False, False]

# draw the initial display
draw_display()

while True:
    # starts or stops the program
    if drone.l2_pressed():
        if not debounce[3]:
            debounce[3] = True
            drone.controller_clear_screen()
            drone.controller_draw_string(0, 5, "Goodbye!")
            break
    else:
        debounce[3] = False

    # select next
    if drone.r1_pressed():
        # without debounce, this function will get called many times for one press
        # use the debounce to make sure only one action is taken for one press
        if not debounce[0]:
            # modulus (%) operator gets the remainder, e.g. 3 % 2 = 1
            # this way if we hit next on last page, it switches back to page 0
            current_sel = (current_sel + 1) % len(songs)

            # we need to redraw the display every time we make a display
            # we don't want to constantly refresh because it takes a bit to draw the screen
            draw_display()
            debounce[0] = True
    else:
        debounce[0] = False

    # select previous
    if drone.l1_pressed():
        if not debounce[1]:
            current_sel = (current_sel - 1) % len(songs)
            draw_display()
            debounce[1] = True
    else:
        debounce[1] = False

    # select song, start playing
    if drone.r2_pressed():
        if not debounce[2]:
            debounce[2] = True
            play_song(songs[current_sel])
            draw_display()
    else:
        debounce[2] = False

    # go to next page
    if drone.up_arrow_pressed():
        if not debounce[4]:
            curr_page = (curr_page - 1) % total_pages
            debounce[4] = True
            draw_display()
    else:
        debounce[4] = False

    # go to previous page
    if drone.down_arrow_pressed():
        if not debounce[5]:
            curr_page = (curr_page + 1) % total_pages
            debounce[5] = True
            draw_display()
    else:
        debounce[5] = False

drone.close()
