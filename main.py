from app import MainApp
from threading import Thread
from database import Database
from time import sleep
from statistics import fmean
from math import sqrt

TEST_SECONDS = 5

db = Database("user_emg.json")
app = MainApp(db)

def interaction():
    app.app_started_lock.acquire()
    while True:
        sleep(0.1)
        app.show_user_view = True
        app.show_bar = False
        app.show_box = False
        app.should_play_video = False

        if not app.user_view.active:
            app.wait_for_enter()
            if not db.check_user_exists(app.user_view.text):
                app.show_user_view = False
                mvc, _ = run_measurement("MVC")
                sleep(2)
                initial, _ = run_measurement("INITIAL", check_sensor=False)
                db.add_user(app.user_view.text, mvc, initial)
            app.show_user_view = True
            app.wait_for_enter()
            app.show_user_view = False
            measurement, arm = run_measurement("NORMAL")
            db.add_user_measurement(app.user_view.text, measurement, arm)
            app.user_view.update_measurements()
            app.show_user_view = True

def run_measurement(mtype, check_sensor = True):
    app.should_play_video = False
    app.show_box = True
    app.show_bar = True
    if check_sensor:
        app.info_text = f"Φορέστε τον αισθητήρα όπως στο βίντεο και πιέστε ENTER."
        app.play_video("videos/instructions.mp4")
        while True:
            app.wait_for_enter()
            if app.wearing_sensor():
                break
    app.should_play_video = False
    app.draw_skeleton = True

    while app.angle_in_range():
        sleep(0.1)

    if mtype == "NORMAL":
        app.info_text = "Αφήστε το χέρι ελεύθερο κάτω και σηκώστε το σε γωνία 90 μοιρών" \
        " με το βαράκι για 5\" για να ξεκινήσει η καταγραφή"
    elif mtype == "MVC":
        app.info_text = "Αφήστε το χέρι ελεύθερο κάτω και σηκώστε το σε γωνία 90 μοιρών \n" \
        " σφίγγοντας όσο πιο δυνατά μπορείτε για 5\" για να καταγραφεί η τιμή MVC σας."
    elif mtype == "INITIAL":
        app.info_text = "Αφήστε το χέρι ελεύθερο κάτω και σηκώστε το σε γωνία 90 μοιρών \n" \
        " με το βαράκι για 5\" για να καταγραφεί η τιμή αναφοράς σας."
    success = False
    while not success:
        app.should_play_video = True
        app.play_video("videos/exercise.mp4")
        app.show_box = True
        arm = app.wait_for_angle()
        app.measuring = True
        app.measurements.clear()
        for i in range(0, TEST_SECONDS * 1000, 100):
            if not app.angle_in_range():
                app.measuring = False
                break
            app.should_play_video = False
            app.show_box = False
            app.seconds = (i / 1000)
            sleep(0.1)
        else:
            success = True
    app.measuring = False
    measurements = sqrt(fmean(app.measurements or [0]))
    print(app.user_view.text, arm, measurements)
    app.show_box = False
    return measurements, arm.value # type: ignore
    

if __name__ == "__main__":
    Thread(None, interaction).start()
    app.start()