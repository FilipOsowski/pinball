from __future__ import division

class Animator:
    def __init__(self, frame_d, animate_f):
        self.frame_duration = frame_d
        self.animate_function = animate_f
        self.current_frame = 0

    def is_done(self):
        if self.current_frame == self.frame_duration:
            return True
        else:
            return False

    def animate(self):
        self.current_frame += 1
        self.animate_function(self.current_frame/self.frame_duration)
