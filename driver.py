from pynput.keyboard import Key, Listener
from sabertooth import *
from sql.sql_config import *
import keyboard




class Driver(Sabertooth):
    def __init__(self):
        super(Driver, self).__init__()
        self.last_err = 1
        self.speed_ratio = 10

    ## this function uses the 2 following functions to preform a manuever in when given a driving distance and rotating
    ## angle. first it rotates and then drives.
    def handle_command(self, angle, distance=5, rotation_speed=50, driving_speed=50):
        try:
            print("angle in driver is {}, distance is {} and speed is {}".format(angle, distance, driving_speed))
            # print ("Vehcile rotating in {} degrees for distance {} in speed {}".format(angle, distance, driving_speed))

            self.rotate_in_angle(angle, rotation_speed)
            self.drive_distance(distance, driving_speed)
        except Exception as e:
            self.saber.stop()
            raise e

    # def rotate_in_angle(self, angle, speed):
    #     print("rotation speed {}".format(speed))
    #     self.turn_left(speed, 1.5, False)
    ## this function uses the readings from the pixhawk to determine how much the robot needs to turn.
    ## it gets the initial heading and calculates the final heading. when it reaches the final heading the robot stops.
    def rotate_in_angle(self, angle, speed=100):
        values_for_mean = 5
        if speed == 0:
            return
        try:
            vals = get_top_table_elem(cursor, "heading_", "SensorsInfo", values_for_mean)
            initial_heading = [int(item) for item in vals]
            initial_heading = sum(initial_heading)/len(initial_heading)

            curr = initial_heading
            diff = 0
            is_at_edge = False
            target = (initial_heading + angle) % 360

            while diff < self.last_err * abs(angle):
                last = curr
                vals = get_top_table_elem(cursor, "heading_", "SensorsInfo", values_for_mean)
                curr = [int(item) for item in vals]
                curr = sum(curr) / len(curr)
                if abs(last - curr) > 300:
                    is_at_edge = True
                if is_at_edge:
                    diff = 360 - abs(initial_heading - curr)
                else:
                    diff = abs(initial_heading - curr)

                # print("diff is {}".format(diff))
                if diff >= 0.95 * abs(angle):
                    break
                err = abs(angle) - diff
                ctl_speed = int(speed * err / abs(angle)) + 15
                if ctl_speed < 30:
                    ctl_speed = 30
                if angle < 0:  # rotate left
                    print("left with speed {}".format(ctl_speed))
                    self.turn_left(ctl_speed, 2, True)
                else:
                    print("right with speed {}".format(ctl_speed))
                    self.turn_right(ctl_speed, 2, True)
            driver.stop()

            vals = get_top_table_elem(cursor, "heading_", "SensorsInfo", values_for_mean)
            finished_actual = [int(item) for item in vals]
            finished_actual = sum(finished_actual)/len(finished_actual)
            if is_at_edge:
                finished_diff = 360 - abs(initial_heading - finished_actual)
            else:
                finished_diff = abs(initial_heading - finished_actual)

            self.last_err = self.last_err * (abs(angle) / finished_diff)

        except Exception as e:
            self.stop()
            raise e
        self.stop()

    ## this function calculates the duration of the drive according to the length needed to be driven.
    def drive_distance(self, distance, speed=100):
        print("speed in drive distance is {}".format(speed))
        if speed == 0:
            return
        dur = distance / (speed * self.speed_ratio)
        try:
            print("driving speed {}".format(speed))
            self.drive_forward(speed, duration=dur)
            self.stop()
            # while time.time() - start < 5:
            #     if distance < 0:  # drive backward
            #         self.saber.drive_backwards(speed)
            #     else:
            #         self.saber.drive_forward(speed)
        except Exception as e:
            self.stop()
            raise e
        self.stop()


if __name__ == '__main__':
    ## the driver module forever awates driving and lifting commands.
    ## when a driving command is loaded to the SQL, the driver parses it and extracts the speed,distance and angle of driving.
    ## the driver then uses the above functions to send the commands to the lynxmotion and sabertooth modules.
    conn, cursor = connect_to_db()
    init_database(cursor, conn)
    init_sql_table(cursor, conn, "driver", d_driver, False)

    update_sql(cursor, conn, "driver", (90, 60, 5, "0"), False, d_driver)
    update_sql(cursor, conn, "driver", (90, 60, 5, "0"), False, d_driver)
    update_sql(cursor, conn, "driver", (90, 60, 5, "0"), False, d_driver)
    update_sql(cursor, conn, "driver", (90, 60, 5, "0"), False, d_driver)
    update_sql(cursor, conn, "driver", (90, 60, 5, "0"), False, d_driver)
    update_sql(cursor, conn, "driver", (90, 60, 5, "0"), False, d_driver)
    print_sql_row(cursor, "driver")

    driver = Driver()
    while True:
        try:
            curr_ID ,new_command = get_row_by_condition(cursor, "is_commited=0", "driver")
            print(new_command)
            if new_command is None:
                continue

            angle_ = get_column_idx(cursor, "driver", "angle")
            angle = new_command[0][angle_]
            speed_ = get_column_idx(cursor, "driver", "speed")
            speed = new_command[0][speed_]
            distance_ = get_column_idx(cursor, "driver", "distance")
            distance = new_command[0][distance_]
            try:
                driver.handle_command(int(angle), int(distance), int(speed), int(speed))
                print("finished command?")
            except Exception as drv_cmd_err:
                print("driving command with ID={} failed".format(curr_ID))
                raise drv_cmd_err
            print("finished command?!")
            set_element_in_row(cursor, "is_commited", curr_ID, "driver", "1")
        except Exception as e:
            driver.stop()
        if keyboard.is_pressed('q'):
            driver.stop()

