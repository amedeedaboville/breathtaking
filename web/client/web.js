webcamError = function() {
  console.log("WEBCAM ERROR.");
}

Meteor.startup(function() {
  ROIAvg = 0;
  d4();
  canvasSource = $("#source")[0];
  canvasBlended = $("#blended")[0];

  //contextSource = canvasSource.getContext('2d');
  contextBlended = canvasBlended.getContext('2d');

  video = $('#webcam')[0];
  width = video.width;
  height = video.height;
  w = Math.floor(width/3);
  h = Math.floor(height/3);
  x = Math.floor(width/2-w/2);
  y = Math.floor(height-h);

	canvas = $("#blended")[0];
  context = canvas.getContext("2d");



  // Get the webcam's stream.
  navigator.getMedia = ( navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia ||
    navigator.msGetUserMedia);

  buffers = [];
  buffidx = 0;

  for (var i = 0; i < 2; i++) {
    buffers.push(new Uint8Array(width * height));
  }
  lastImageData = null;

  console.log("startup");
  if (navigator.getMedia) {
    navigator.getMedia({video: true}, startStream, webcamError);
  }
  else { console.log('Native web camera streaming (getUserMedia) is not supported in this browser.'); }
})

function startStream(stream) {
  video.src = URL.createObjectURL(stream);
  video.play();

  requestAnimationFrame(draw);
}

function draw() {
  var frame = readFrame();
  if (frame) {
    markLightnessChanges(frame.data);
    context.putImageData(frame, 0, 0);
    context.rect(x,y,w,h);
    context.stroke();
    getROIAvg();
  }
  requestAnimationFrame(draw); // Wait for the next frame.
}

function getROIAvg() {
  var data = buffers[buffidx% buffers.length];
  var sum = 0;
  for(var i = x; i < x + w; i++)
    for(var j = y; j < y+ h; j++) {
      sum += data[j + i*width]; 
    }
  ROIAvg = sum/(w*h + 1);
}
function readFrame() {
  try { context.drawImage(video, 0, 0, width, height); } 
  catch (e) {
    return null; // The video may not be ready, yet.
  }

  return context.getImageData(0, 0, width, height);
}

function markLightnessChanges(data) {
  // Pick the next buffer (round-robin).
  var buffer = buffers[buffidx++ % buffers.length];

  for (var i = 0, j = 0; i < buffer.length; i++, j += 4) {
    // Determine lightness value.
    var current = lightnessValue(data[j], data[j + 1], data[j + 2]);

    // Set color to black.
    data[j] = data[j + 1] = data[j + 2] = 0;

    // Full opacity for changes.
    data[j + 3] = 255 * lightnessHasChanged(i, current);

    // Store current lightness value.
    buffer[i] = current;
  }
}

function lightnessHasChanged(index, value) {
  return buffers.some(function (buffer) {
    return Math.abs(value - buffer[index]) >= 15;
  });
}

function lightnessValue(r, g, b) {
  return (Math.min(r, g, b) + Math.max(r, g, b)) / 255 * 50;
}

Template.hello.greeting = function () {
  return "Welcome to web.";
};


Template.hello.events({
  'click input' : function () {
    // template data, if any, is available in 'this'
    if (typeof console !== 'undefined')
  console.log("You pressed the button");
  }
});
