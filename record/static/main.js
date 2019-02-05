var socket = io.connect('http://' + document.domain + ':' + location.port);
$('button').on('click', function(event){
  socket.emit('record');
})


