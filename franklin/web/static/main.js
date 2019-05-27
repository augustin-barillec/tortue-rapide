const socket = io.connect('http://' + document.domain + ':' + location.port);
// Timeout gamepad loop in ms
const gamePadLoopTimeout = 100;
const checkTimeout = 1000;

let isRecording = false;
let isAutoPilot = false;
let gamePadOutSent = false;
let throttle = 0;

$(document).ready(function () {
  $(".GaugeMeter").gaugeMeter();

  // $(document).on("keydown", function(e){
  //   if isA
  // });

  $("#record_toggle").on("change", function (e) {
    if (this.checked) socket.emit("start_recording");
    else socket.emit("stop_recording");
    isRecording = !isRecording;
  });

  $("#pilot_toggle").on("change", function (e) {
    if (this.checked) socket.emit("start_pilot");
    else socket.emit("stop_pilot");
    isAutoPilot = !isAutoPilot;
    isRecording = false;
  });

  socket.on("latest_image", function(data) {
    console.log(`latest image received: \n ${data}`);
  });

  function gamePadLoop() {
    setTimeout(gamePadLoop, gamePadLoopTimeout);

    const pad = navigator.getGamepads()[0];

    // Send the gamepad_out message once
    if (!pad) {
      if (!gamePadOutSent) {
        socket.emit("gamepad_out");
        gamePadOutSent = true;
      }
      // TODO: pretty error message
      return;
    }

    if(isRecording) {
      angle = pad.axes[0];
      throttle = pad.axes[3];
      socket.emit("gamepad_input", angle, throttle);
    }
    
    if(gamePadOutSent) gamePadOutSent = false;
  }
  gamePadLoop();

  function healthcheck() {
    setTimeout(healthcheck, checkTimeout);
    socket.emit("healthcheck");
  }
  healthcheck();
});