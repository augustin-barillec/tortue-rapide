const socket = io.connect('http://' + document.domain + ':' + location.port);
// Timeout gamepad loop in ms
const gamePadLoopTimeout = 1000;

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

  // function check() {
  //   setTimeout(check, 2000);
  //   socket.emit("check");
  // }
  // check();
});