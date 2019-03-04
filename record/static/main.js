var isRecording = false;

var socket = io.connect('http://' + document.domain + ':' + location.port);

$(document).on("keydown", function (event) {
  console.log("viznpvo");
  if (!isRecording) return;

  switch (event.which) {
    case 38:
      socket.emit("input_change", { val: "UP" });
      break;
    case 40:
      socket.emit("input_change", { val: "DOWN" });
      break;
    case 37:
      socket.emit("input_change", { val: "LEFT" });
      break;
    case 39:
      socket.emit("input_change", { val: "RIGHT" });
      break;
    default:
      break;
  }

});

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
});