const socket = io.connect('http://' + document.domain + ':' + location.port);
// Timeout gamepad loop in ms
const gamePadLoopTimeout = 1000;
const checkTimeout = 1000;

var isRecording = false;

$(document).ready(function () {
  $("#record_toggle").on("change", function (e) {
    if (this.checked) {
      socket.emit("start_recording");
    }
    else {
      socket.emit("stop_recording");
    }
    isRecording = !isRecording;
  });

  socket.on("latest_image", function(data) {
    console.log(`latest image received: \n ${data}`);
  });

  function gamePadLoop() {
    setTimeout(gamePadLoop, gamePadLoopTimeout);
    if(isRecording) {
      const pad = navigator.getGamepads()[0];
      console.log(pad);
      if (!pad) {
        socket.emit("gamepad_out");
        // TODO: pretty error message
        return;
      }
      angle = pad.axes[0];
      throttle = pad.axes[3];
      socket.emit("gamepad_input", angle, throttle);
    }
  }
  gamePadLoop();

  function healthcheck() {
    setTimeout(healthcheck, checkTimeout);
    socket.emit("healthcheck");
  }
  healthcheck();
});