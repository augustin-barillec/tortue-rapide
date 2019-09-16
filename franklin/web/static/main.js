const socket = io.connect('http://' + document.domain + ':' + location.port);
// Timeout gamepad loop in ms
const gamePadLoopTimeout = 100;
const checkTimeout = 1000;

let isRecording = false;
let isAutoPilot = false;
let gamePadOutSent = false;
let throttle = 0;

function extend_array(a, b) {
  for (let i = 0; i < b.length; i++) {
    a.push(b[i])
  }
  return a
}

$(document).ready(function () {
  // Get the exising models on start, use refresh_models_list button to refresh
  let models_list = []
  const no_model = "No model (manual)"
  fill_models_list("get_models_list")

  function fill_models_list(to_emit) {
    // Delete all the options
    var select = $("#models");
    select.find("option").remove()
    // Always start with the "no model" option
    models_list = [no_model]

    // Get the new list of models
    socket.emit(to_emit, function (list) {
      models_list = extend_array(models_list, list);
      // Add the new list as options
      $.each(models_list, function (index, item) {
        select.append(new Option(item, item));
      });
    })
  }

  $(".GaugeMeter").gaugeMeter();

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

  $("#models").on("change", function(event) {
    const options_value = $(event.currentTarget).val()
    const value = options_value === no_model ? "" : options_value
    socket.emit("set_model", value)
  })

  $("#refresh_models_list").on("click", function (e) {
    fill_models_list("refresh_models_list");
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

    if (isRecording) {
      throttle = -pad.axes[1];
      angle = pad.axes[2];
      socket.emit("gamepad_input", angle, throttle);
    }

    if (gamePadOutSent) gamePadOutSent = false;
  }
  gamePadLoop();

  function healthcheck() {
    setTimeout(healthcheck, checkTimeout);
    socket.emit("healthcheck");
  }
  healthcheck();
});