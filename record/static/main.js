var socket = io.connect('http://' + document.domain + ':' + location.port);
var a = 0
$('button#record_button').on('click', function(){
  a = !a
  socket.emit('record', {a: a});
})


