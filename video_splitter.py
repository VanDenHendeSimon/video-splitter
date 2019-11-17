"""
Download codecs from here ↓
https://www.codecguide.com/download_kl_old.htm#xp_last_version
"""

import sys
from PySide2 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('Video Splitter')

        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player = QtMultimedia.QMediaPlayer()

        # Setting QToolBar
        tool_bar = QtWidgets.QToolBar()
        tool_bar.setWindowTitle('Toolbar')
        self.addToolBar(tool_bar)

        file_menu = self.menuBar().addMenu("&File")

        # Define actions for in the file menu
        open_action = QtWidgets.QAction(
            "Open",
            self,
            shortcut="Ctrl+O",
            triggered=self.open
        )
        exit_action = QtWidgets.QAction(
            "E&xit",
            self,
            shortcut="Ctrl+Q",
            triggered=QtWidgets.QApplication.instance().quit
        )

        file_menu.addAction(open_action)
        file_menu.addAction(exit_action)

        play_menu = self.menuBar().addMenu("&Play")

        # add icons and actions
        # Play
        play_icon = self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)
        self.play_action = tool_bar.addAction(play_icon, "Play")
        self.play_action.triggered.connect(self.player.play)
        play_menu.addAction(self.play_action)

        # Pause
        pause_icon = self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause)
        self.pause_action = tool_bar.addAction(pause_icon, "Pause")
        self.pause_action.triggered.connect(self.player.pause)
        play_menu.addAction(self.pause_action)

        # Stop
        stop_icon = self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop)
        self.stop_action = tool_bar.addAction(stop_icon, "Stop")
        self.stop_action.triggered.connect(self.player.stop)
        play_menu.addAction(self.stop_action)

        # Previous
        previous_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_MediaSkipBackward
        )
        self.previous_action = tool_bar.addAction(previous_icon, "Previous")
        self.previous_action.triggered.connect(self.previous_clicked)
        play_menu.addAction(self.previous_action)

        # Next
        next_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_MediaSkipForward
        )
        self.next_action = tool_bar.addAction(next_icon, "Next")
        self.next_action.triggered.connect(self.playlist.next)
        play_menu.addAction(self.next_action)

        # About menu
        about_menu = self.menuBar().addMenu("&About")
        about_qt_action = QtWidgets.QAction("About &Qt", self)
        about_menu.addAction(about_qt_action)

        # Create video widget
        self.video_widget = QtMultimediaWidgets.QVideoWidget()

        # Create widget that will contain all of the UI elements
        self.window_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.window_widget)

        # add slider to control volume
        self.vol_slider = QtWidgets.QSlider()
        self.vol_slider.setOrientation(QtGui.Qt.Horizontal)
        self.vol_slider.setMinimum(0)
        self.vol_slider.setMaximum(100)
        self.vol_slider.setFixedWidth(120)
        self.vol_slider.setValue(self.player.volume())
        self.vol_slider.setTickInterval(10)
        self.vol_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.vol_slider.setToolTip("Volume")
        self.vol_slider.valueChanged.connect(self.player.setVolume)

        tool_bar.addSeparator()
        tool_bar.addWidget(self.vol_slider)
        tool_bar.addSeparator()

        # Split
        split_icon = self.style().standardIcon(QtWidgets.QStyle.SP_ArrowDown)
        self.split_action = tool_bar.addAction(split_icon, 'Split')
        self.split_action.triggered.connect(self.split)

        tool_bar.addSeparator()

        self.speed_slider = QtWidgets.QSlider()
        self.speed_slider.setOrientation(QtGui.Qt.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(200)
        self.speed_slider.setValue(100)
        self.speed_slider.setFixedWidth(120)
        self.speed_slider.setToolTip("Speed")
        self.speed_slider.valueChanged.connect(self.set_speed)

        self.speed_label = QtWidgets.QLabel(
            '  ' + str(self.speed_slider.value()/100) + 'x'
        )

        tool_bar.addWidget(self.speed_slider)
        tool_bar.addWidget(self.speed_label)

        # BOTTOM STUFF

        # Time slider
        self.time_slider = QtWidgets.QSlider()
        self.time_slider.setOrientation(QtGui.Qt.Horizontal)
        self.time_slider.setRange(0, 0)

        # Empty layout to store all cuts
        self.cuts_layout = QtWidgets.QVBoxLayout()

        # Details under the slider
        self.time_details = QtWidgets.QHBoxLayout()
        self.current_label = QtWidgets.QLabel('')
        self.duration_label = QtWidgets.QLabel('')

        self.current_label.setFixedHeight(9)
        self.duration_label.setFixedHeight(9)

        self.time_details.addWidget(self.current_label)
        self.time_details.addStretch(1)
        self.time_details.addWidget(self.duration_label)

        # MAIN UI WINDOW LAYOUT
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.video_widget)
        self.main_layout.addWidget(self.time_slider)
        self.main_layout.addLayout(self.time_details)
        self.main_layout.addLayout(self.cuts_layout)

        self.window_widget.setLayout(self.main_layout)

        self.player.setPlaylist(self.playlist)
        self.player.stateChanged.connect(self.update_buttons)
        self.player.setVideoOutput(self.video_widget)

        self.update_buttons(self.player.state())

        # Initialize duration and current (both represented in milliseconds)
        self.duration = 0
        self.current = 0
        self.cuts = []

        self.player.positionChanged.connect(self.position_changed)
        self.time_slider.valueChanged.connect(self.set_position)

    def set_speed(self):
        self.player.setPlaybackRate(self.speed_slider.value()/100)
        self.speed_label.setText(
            '  ' + str(self.speed_slider.value()/100) + 'x'
        )

    def split(self):
        """
        This function is triggered when the user clicks
        the button to split the video.
        A QProgressBar will be added, as well as pre- and suffix QLineEdits.

        Lastly, a button is added,
        which will allow the user to overwrite this cut later.
        """
        self.cuts.append(self.current)

        # add a bar
        bar = QtWidgets.QProgressBar()
        bar.setRange(0, self.duration)
        bar.setStyleSheet(
            " QProgressBar { border: 1px solid grey; text-align: center;}"
            " QProgressBar::chunk {background-color: #3add36; width: 1px;}"
        )
        bar.setValue(self.current)
        bar.setFormat(format_milliseconds(self.current))
        # add pre and suffix inputs
        pre_and_suffix_layout = QtWidgets.QHBoxLayout()
        prefix_label = QtWidgets.QLabel('Prefix: ')
        prefix = QtWidgets.QLineEdit()

        suffix_label = QtWidgets.QLabel('Suffix: ')
        suffix = QtWidgets.QLineEdit()

        # add button to update cut later
        update_button = QtWidgets.QPushButton('Update Cut')
        update_button.clicked.connect(lambda: self.update_cut(bar))

        # add all of these things to a QHBoxLayout
        pre_and_suffix_layout.addWidget(prefix_label)
        pre_and_suffix_layout.addWidget(prefix)
        pre_and_suffix_layout.addStretch()
        pre_and_suffix_layout.addWidget(suffix_label)
        pre_and_suffix_layout.addWidget(suffix)
        pre_and_suffix_layout.addWidget(update_button)

        # add this horizontal layout to the vertical layout under the video
        self.cuts_layout.addWidget(bar)
        self.cuts_layout.addLayout(pre_and_suffix_layout)

    def update_cut(self, cut):
        """
        This function gets executed whenever
        the 'update cut' button is pressed.
        The current position in time will be set as
        the new value of the bar and the list
        :param cut: QProgressbar object that is linked to this button
        """
        # Remove initial cut from the list
        self.cuts.remove(cut.value())
        # Update the progress bar
        cut.setValue(self.current)
        # Update the text in the bar
        cut.setFormat(format_milliseconds(self.current))
        # Add current time to the list
        self.cuts.append(cut.value())

    def position_changed(self, position):
        """
        This function will be triggered automatically
        whenever a change in position in time is detected.
        This function will then set the following variables
            - self.current
            - self.current_label
            - self.time_slider (value)
        :param position: position in time, in milliseconds
        """
        # Set global variable for position in time
        self.current = position

        # Set value in the time slider
        self.time_slider.setValue(position)

        # Set the label in the UI
        self.current_label.setText('%d/%d (%s)' % (
            position, self.duration, format_milliseconds(position)
        ))

    def set_position(self, origin="timeslider"):
        """
        Update the time-position of the video
        :param origin: where this function is called from
        :return:
        """
        # Only update the position like this when video is paused
        if self.player.state() != QtMultimedia.QMediaPlayer.PlayingState:
            if origin != "keypressed":
                # Fetch current value of the time slider
                # Unless function is called from keypressed method
                self.current = self.time_slider.value()
            # Time slider value, which is mapped to the duration of the video,
            # becomes the new position

            # Unless function is called from keypressed method,
            # then self.current is already set correctly
            self.player.setPosition(self.current)

    def set_duration(self, dur):
        """
        This function gets triggered whenever a different video starts playing.
        A change of duration is detected
        and this function will take care of (re)setting the right variables
        :param dur: duration of the currently playing video in milliseconds
        """
        # Set global variable for duration
        self.duration = dur

        # Set the range of the time slider
        self.time_slider.setRange(0, dur)

        # Set duration label text in the UI
        self.duration_label.setText(format_milliseconds(dur))

    def open(self):
        """
        This function will prompt the user with a file browsing dialog.
        The selected video will then be added to the list of videos.
        Afterwards, we switch to this newly added video,
        update the duration variable and start playback.
        """
        file_dialog = QtWidgets.QFileDialog(self)

        supported_mime_types = ["video/mp4", "*.*"]
        file_dialog.setMimeTypeFilters(supported_mime_types)
        movies_location = QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.MoviesLocation
        )
        file_dialog.setDirectory(movies_location)

        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            # Add newly selected video
            self.playlist.addMedia(file_dialog.selectedUrls()[0])
            # Go to the new video's index in the playlist
            self.playlist.next()
            # Trigger re-fetching of the duration to update timeline
            self.player.durationChanged.connect(self.set_duration)
            # Play the video
            self.player.play()

    def previous_clicked(self):
        """
        Go to the previous video in the media list,
        unless we are within the first 5sec of the currently playing video.

        If we are, restart the currently playing video,
        if we are passed the 5sec mark, go to the previous movie in the list.

        We do not have to check whether there are multiple videos in this list,
        since the button will be dynamically enabled/disabled.
        """
        # Go to previous track if we are within the first 5 seconds of playback
        # Otherwise, seek to the beginning.
        if self.player.position() <= 5000:
            self.playlist.previous()
        else:
            self.player.setPosition(0)

    def keyPressEvent(self, event):
        """
        Allow the user to go frame by frame by assigning the '[' and ']' keys.
        frames per second is assumed to be 24,
        which is mostly used for video encoding along with 25 and 30.

        Since this is not perfect/streamlined,
        video's can be cut on non-integer frames,

        but that is not as bad as it seems.
        For very detailed / accurate cutting you can use
        Software like Adobe Premiere/After Effects.
        For basic video cutting this feature will suffice,
        as well as the scrolling feature that comes with the QSlider

        :param event: event.key() will yield the ascii code of the pressed key
        """
        # Assume fps to be 24
        fps = 1 / 24 * 1000
        if event.key() == 91:   # [
            self.current = (self.player.position() - fps)
        elif event.key() == 93:  # ]
            self.current = (self.player.position() + fps)
        elif event.key() == 83:  # s
            self.split()

        self.set_position("keypressed")

    def update_buttons(self, state):
        """
        Update the buttons when the state of the QMediaPlayer changes.
        This function will enable/disable all of the play menu actions,
        so that these match the current state of the playback.

        This function is triggered dynamically every time this state changes.
        It is also ran when the program starts to initialize the buttons.

        :param state: Current state of the QMediaPlayer
        """
        media_count = self.playlist.mediaCount()
        self.play_action.setEnabled(
            media_count > 0 and state != QtMultimedia.QMediaPlayer.PlayingState
        )
        self.pause_action.setEnabled(
            state == QtMultimedia.QMediaPlayer.PlayingState
        )
        self.stop_action.setEnabled(
            state != QtMultimedia.QMediaPlayer.StoppedState
        )
        self.previous_action.setEnabled(self.player.position() > 0)
        self.next_action.setEnabled(media_count > 1)


def format_milliseconds(ms):
    hours, remainder = divmod((ms / 1000), 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()
    sys.exit(app.exec_())
