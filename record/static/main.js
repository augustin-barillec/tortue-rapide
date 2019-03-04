var socket = io.connect('http://' + document.domain + ':' + location.port);

$(document).ready(function () {
  $("#record_button").on("change", function (e) {
    if(this.checked) socket.emit("start_recording");
    else socket.emit("stop_recording");
  });
});