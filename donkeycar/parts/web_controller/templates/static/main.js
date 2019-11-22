var driveHandler = new function() {
    //functions used to drive the vehicle.

    var state = {'tele': {
                          "user": {
                                  'angle': 0,
                                  'throttle': 0,
                                  },
                          "pilot": {
                                  'angle': 0,
                                  'throttle': 0,
                                  }
                          },
                  'brakeOn': true,
                  'recording': false,
                  'driveMode': "user",
                  'pilot': 'None',
                  'session': 'None',
                  'lag': 0,
                  'controlMode': 'joystick',
                  'maxThrottle' : 1,
                  'throttleMode' : 'user',
                  }

    var joystick_options = {}
    var joystickLoopRunning=false;

    var hasGamepad = false;

    var deviceHasOrientation=false;
    var initialGamma;

    var vehicle_id = ""
    var driveURL = ""
    var vehicleURL = ""

    this.load = function() {
      driveURL = '/drive'
      vehicleURL = '/drive'

      setBindings()

      joystick_options = {
        zone: document.getElementById('joystick_container'),  // active zone
        color: '#668AED',
        size: 350,
      };

      var manager = nipplejs.create(joystick_options);
      bindNipple(manager)

      if(!!navigator.getGamepads){
        console.log("Device has gamepad support.")
        hasGamepad = true;
      }

      if (window.DeviceOrientationEvent) {
        window.addEventListener("deviceorientation", handleOrientation);
        console.log("Browser supports device orientation, setting control mode to tilt.");
        state.controlMode = 'tilt';
        deviceOrientationLoop();
      } else {
        console.log("Device Orientation not supported by browser, setting control mode to joystick.");
        state.controlMode = 'joystick';
      }
    };


    var setBindings = function() {

      $(document).keydown(function(e) {
          if(e.which == 32) { toggleBrake() }  // 'space'  brake
          // if(e.which == 82) { toggleRecording() }  // 'r'  toggle recording
          if(e.which == 38) { throttleUp() }  // 'i'  throttle up
          if(e.which == 40) { throttleDown() } // 'k'  slow down
          if(e.which == 37) { angleLeft() } // 'j' turn left
          if(e.which == 39) { angleRight() } // 'l' turn right
          // if(e.which == 65) { updateDriveMode('auto') } // 'a' turn on auto mode
          // if(e.which == 68) { updateDriveMode('user') } // 'd' turn on manual mode
          // if(e.which == 83) { updateDriveMode('auto_angle') } // 'a' turn on auto mode
      });


      $('#pilot_select').on('change', function () {
        state.pilot = $(this).val(); // get selected value
        postPilot()
      });

      $('#mode_select').on('change', function () {
        updateDriveMode($(this).val());
      });

      $('#max_throttle_select').on('change', function () {
        state.maxThrottle = parseFloat($(this).val());
      });

      $('#throttle_mode_select').on('change', function () {
        state.throttleMode = $(this).val();
      });

      $('#record_button').click(function () {
        toggleRecording();
      });

      $('#brake_button').click(function() {
        toggleBrake();
      });

      $('input[type=radio][name=controlMode]').change(function() {
        if (this.value == 'joystick') {
          state.controlMode = "joystick";
          joystickLoopRunning = true;
          console.log('joystick mode');
          joystickLoop();
        } else if (this.value == 'tilt' && deviceHasOrientation) {
          joystickLoopRunning = false;
          state.controlMode = "tilt";
          console.log('tilt mode')
        } else if (this.value == 'gamepad' && hasGamepad) {
          joystickLoopRunning = false;
          state.controlMode = "gamepad";
          console.log('gamepad mode')
          gamePadLoop();
        }
        updateUI();
      });

    };

    ////////////////////////////////////////// ARROWS
    $(document).keydown(function(e) {
      if (e.which==37) {
        $('.left').addClass('pressed');
        $('.lefttext').text('LEFT');
        $('.left').css('transform', 'translate(0, 2px)');
      } else if (e.which==38) {
        $('.up').addClass('pressed');
        $('.uptext').text('UP');
        $('.left').css('transform', 'translate(0, 2px)');
        $('.down').css('transform', 'translate(0, 2px)');
        $('.right').css('transform', 'translate(0, 2px)');
      } else if (e.which==39) {
        $('.right').addClass('pressed');
        $('.righttext').text('RIGHT');
        $('.right').css('transform', 'translate(0, 2px)');
      } else if (e.which==40) {
        $('.down').addClass('pressed');
        $('.downtext').text('DOWN');
        $('.down').css('transform', 'translate(0, 2px)');
      } else if (e.which==66) {
        $('.b').text('B');
      } else if (e.which==65) {
        $('.a').text('A');
      }
    });

    $(document).keyup(function(e) {
      if (e.which==37) {
        $('.left').removeClass('pressed');
        $('.lefttext').text('');
        $('.left').css('transform', 'translate(0, 0)');
      } else if (e.which==38) {
        $('.up').removeClass('pressed');
        $('.uptext').text('');
        $('.left').css('transform', 'translate(0, 0)');
        $('.down').css('transform', 'translate(0, 0)');
        $('.right').css('transform', 'translate(0, 0)');
      } else if (e.which==39) {
        $('.right').removeClass('pressed');
        $('.righttext').text('');
        $('.right').css('transform', 'translate(0, 0)');
      } else if (e.which==40) {
        $('.down').removeClass('pressed');
        $('.downtext').text('');
        $('.down').css('transform', 'translate(0, 0)');
      } else if (e.which==66) {
        $('.b').text('');
      } else if (e.which==65) {
        $('.a').text('');
      }
    });

    $('.left').mousedown(function() {
      $('.lefttext').text('LEFT');
      $('.left').css('transform', 'translate(0, 2px)');
    });

    $('.left').mouseup(function() {
      $('.lefttext').text('');
      $('.left').css('transform', 'translate(0, 0)');
    });

    $('.right').mousedown(function() {
      $('.righttext').text('RIGHT');
      $('.right').css('transform', 'translate(0, 2px)');
    });

    $('.right').mouseup(function() {
      $('.righttext').text('');
      $('.right').css('transform', 'translate(0, 0)');
    });

    $('.up').mousedown(function() {
      $('.uptext').text('UP');
      $('.left').css('transform', 'translate(0, 2px)');
      $('.down').css('transform', 'translate(0, 2px)');
      $('.right').css('transform', 'translate(0, 2px)');
    });

    $('.up').mouseup(function() {
      $('.uptext').text('');
      $('.left').css('transform', 'translate(0, 0)');
      $('.down').css('transform', 'translate(0, 0)');
      $('.right').css('transform', 'translate(0, 0)');
    });

    $('.down').mousedown(function() {
      $('.downtext').text('DOWN');
      $('.down').css('transform', 'translate(0, 2px)');
    });

    $('.down').mouseup(function() {
      $('.downtext').text('');
      $('.down').css('transform', 'translate(0, 0)');
    });

    /*
     * Konami-JS ~
     * :: Now with support for touch events and multiple instances for
     * :: those situations that call for multiple easter eggs!
     * Code: https://konami-js.googlecode.com/
     * Examples: http://www.snaptortoise.com/konami-js
     * Copyright (c) 2009 George Mandis (georgemandis.com, snaptortoise.com)
     * Version: 1.4.2 (9/2/2013)
     * Licensed under the MIT License (https://opensource.org/licenses/MIT)
     * Tested in: Safari 4+, Google Chrome 4+, Firefox 3+, IE7+, Mobile Safari 2.2.1 and Dolphin Browser
     */

    var Konami = function (callback) {
      var konami = {
        addEvent: function (obj, type, fn, ref_obj) {
          if (obj.addEventListener)
            obj.addEventListener(type, fn, false);
          else if (obj.attachEvent) {
            // IE
            obj["e" + type + fn] = fn;
            obj[type + fn] = function () {
              obj["e" + type + fn](window.event, ref_obj);
            }
            obj.attachEvent("on" + type, obj[type + fn]);
          }
        },
        input: "",
        pattern: "3838404037393739",
        load: function (link) {
          this.addEvent(document, "keydown", function (e, ref_obj) {
            if (ref_obj) konami = ref_obj; // IE
            konami.input += e ? e.keyCode : event.keyCode;
            if (konami.input.length > konami.pattern.length)
              konami.input = konami.input.substr((konami.input.length - konami.pattern.length));
            if (konami.input == konami.pattern) {
              konami.code(link);
              konami.input = "";
              e.preventDefault();
              return false;
            }
          }, this);
          this.iphone.load(link);
        },
        code: function (link) {
          window.location = link
        },
        iphone: {
          start_x: 0,
          start_y: 0,
          stop_x: 0,
          stop_y: 0,
          tap: false,
          capture: false,
          orig_keys: "",
          keys: ["UP", "UP", "DOWN", "DOWN", "LEFT", "RIGHT", "LEFT", "RIGHT"],
          code: function (link) {
            konami.code(link);
          },
          load: function (link) {
            this.orig_keys = this.keys;
            konami.addEvent(document, "touchmove", function (e) {
              if (e.touches.length == 1 && konami.iphone.capture == true) {
                var touch = e.touches[0];
                konami.iphone.stop_x = touch.pageX;
                konami.iphone.stop_y = touch.pageY;
                konami.iphone.tap = false;
                konami.iphone.capture = false;
                konami.iphone.check_direction();
              }
            });
            konami.addEvent(document, "touchend", function (evt) {
              if (konami.iphone.tap == true) konami.iphone.check_direction(link);
            }, false);
            konami.addEvent(document, "touchstart", function (evt) {
              konami.iphone.start_x = evt.changedTouches[0].pageX;
              konami.iphone.start_y = evt.changedTouches[0].pageY;
              konami.iphone.tap = true;
              konami.iphone.capture = true;
            });
          },
          check_direction: function (link) {
            x_magnitude = Math.abs(this.start_x - this.stop_x);
            y_magnitude = Math.abs(this.start_y - this.stop_y);
            x = ((this.start_x - this.stop_x) < 0) ? "RIGHT" : "LEFT";
            y = ((this.start_y - this.stop_y) < 0) ? "DOWN" : "UP";
            result = (x_magnitude > y_magnitude) ? x : y;
            result = (this.tap == true) ? "TAP" : result;

            if (result == this.keys[0]) this.keys = this.keys.slice(1, this.keys.length);
            if (this.keys.length == 0) {
              this.keys = this.orig_keys;
              this.code(link);
            }
          }
        }
      }

      typeof callback === "string" && konami.load(callback);
      if (typeof callback === "function") {
        konami.code = callback;
        konami.load();
      }

      return konami;
    };

    var easter_egg = new Konami();
    easter_egg.code = function() {
      alert('Colors mode activated (Press A when you close this)!');

      $('.up').css('background', 'orange');
      $('.up').css('border-right', '10px solid #996300');
      $('.up').css('border-bottom', '10px solid #996300');
      $('.up').css('border-left', '10px solid #b37300');
      $('.up').css('border-top', '10px solid #cc8400');
      $('.uptext').css('color', 'orange')
      $('.uptext').css('text-shadow', '0 0 10px orange, 0 0 10px orange, 0 0 10px orange, 0 0 10px orange');

      $('.down').css('background', 'tomato');
      $('.down').css('border-right', '10px solid #e02200');
      $('.down').css('border-bottom', '10px solid #e02200');
      $('.down').css('border-left', '10px solid #f92600');
      $('.down').css('border-top', '10px solid #ff3814');
      $('.downtext').css('color', 'tomato')
      $('.downtext').css('text-shadow', '0 0 10px tomato, 0 0 10px tomato, 0 0 10px tomato, 0 0 10px tomato');

      $('.left').css('background', 'skyblue');
      $('.left').css('border-right', '10px solid #30aadc');
      $('.left').css('border-bottom', '10px solid #30aadc');
      $('.left').css('border-left', '10px solid #45b3e0');
      $('.left').css('border-top', '10px solid #5bbce4');
      $('.lefttext').css('color', 'skyblue')
      $('.lefttext').css('text-shadow', '0 0 10px skyblue, 0 0 10px skyblue, 0 0 10px skyblue, 0 0 10px skyblue');

      $('.right').css('background', 'red');
      $('.right').css('border-right', '10px solid #990000');
      $('.right').css('border-bottom', '10px solid #990000');
      $('.right').css('border-left', '10px solid #b30000');
      $('.right').css('border-top', '10px solid #cc0000');
      $('.righttext').css('color', 'red')
      $('.righttext').css('text-shadow', '0 0 10px red, 0 0 10px red, 0 0 10px red, 0 0 10px red');
    }
    easter_egg.load();
////////////////////////////////////////


    function bindNipple(manager) {
      manager.on('start', function(evt, data) {
        state.tele.user.angle = 0
        state.tele.user.throttle = 0
        state.recording = true
        joystickLoopRunning=true;
        joystickLoop();

      }).on('end', function(evt, data) {
        joystickLoopRunning=false;
        brake()

      }).on('move', function(evt, data) {
        state.brakeOn = false;
        radian = data['angle']['radian']
        distance = data['distance']

        //console.log(data)
        state.tele.user.angle = Math.max(Math.min(Math.cos(radian)/70*distance, 1), -1)
        state.tele.user.throttle = limitedThrottle(Math.max(Math.min(Math.sin(radian)/70*distance , 1), -1))

        if (state.tele.user.throttle < .001) {
          state.tele.user.angle = 0
        }

      });
    }


    var postPilot = function(){
        data = JSON.stringify({ 'pilot': state.pilot })
        $.post(vehicleURL, data)
    }


    var updateUI = function() {
      $("#throttleInput").val(state.tele.user.throttle);
      $("#angleInput").val(state.tele.user.angle);
      $('#mode_select').val(state.driveMode);

      var throttlePercent = Math.round(Math.abs(state.tele.user.throttle) * 100) + '%';
      var steeringPercent = Math.round(Math.abs(state.tele.user.angle) * 100) + '%';
      var throttleRounded = state.tele.user.throttle.toFixed(2)
      var steeringRounded = state.tele.user.angle.toFixed(2)

      $('#throttle_label').html(throttleRounded);
      $('#steering_label').html(steeringRounded);

      if(state.tele.user.throttle < 0) {
        $('#throttle-bar-backward').css('width', throttlePercent).html(throttleRounded)
        $('#throttle-bar-forward').css('width', '0%').html('')
      }
      else if (state.tele.user.throttle > 0) {
        $('#throttle-bar-backward').css('width', '0%').html('')
        $('#throttle-bar-forward').css('width', throttlePercent).html(throttleRounded)
      }
      else {
        $('#throttle-bar-forward').css('width', '0%').html('')
        $('#throttle-bar-backward').css('width', '0%').html('')
      }

      if(state.tele.user.angle < 0) {
        $('#angle-bar-backward').css('width', steeringPercent).html(steeringRounded)
        $('#angle-bar-forward').css('width', '0%').html('')
      }
      else if (state.tele.user.angle > 0) {
        $('#angle-bar-backward').css('width', '0%').html('')
        $('#angle-bar-forward').css('width', steeringPercent).html(steeringRounded)
      }
      else {
        $('#angle-bar-forward').css('width', '0%').html('')
        $('#angle-bar-backward').css('width', '0%').html('')
      }

      if (state.recording) {
        $('#record_button')
          .html('Stop Recording (r)')
          .removeClass('btn-info')
          .addClass('btn-warning').end()
      } else {
        $('#record_button')
          .html('Start Recording (r)')
          .removeClass('btn-warning')
          .addClass('btn-info').end()
      }

      if (state.brakeOn) {
        $('#brake_button')
          .html('Start Vehicle')
          .removeClass('btn-danger')
          .addClass('btn-success').end()
      } else {
        $('#brake_button')
          .html('Stop Vehicle')
          .removeClass('btn-success')
          .addClass('btn-danger').end()
      }

      if(deviceHasOrientation) {
        $('#tilt-toggle').removeAttr("disabled")
        $('#tilt').removeAttr("disabled")
      } else {
        $('#tilt-toggle').attr("disabled", "disabled");
        $('#tilt').prop("disabled", true);
      }

      if(hasGamepad) {
        $('#gamepad-toggle').removeAttr("disabled")
        $('#gamepad').removeAttr("disabled")
      } else {
        $('#gamepad-toggle').attr("disabled", "disabled");
        $('#gamepad').prop("disabled", true);
      }

      if (state.controlMode == "joystick") {
        $('#joystick-column').show();
        $('#tilt-toggle').removeClass("active");
        $('#joystick-toggle').addClass("active");
        $('#joystick').attr("checked", "checked")
        $('#tilt').removeAttr("checked")
      } else if (state.controlMode == "tilt") {
        $('#joystick-column').hide();
        $('#joystick-toggle').removeClass("active");
        $('#tilt-toggle').addClass("active");
        $('#joystick').removeAttr("checked");
        $('#tilt').attr("checked", "checked");
      }

      //drawLine(state.tele.user.angle, state.tele.user.throttle)
    };

    var postDrive = function() {

        //Send angle and throttle values
        data = JSON.stringify({ 'angle': state.tele.user.angle,
                                'throttle':state.tele.user.throttle,
                                'drive_mode':state.driveMode,
                                'recording': state.recording})
        console.log(data)
        $.post(driveURL, data)
        updateUI()
    };

    var applyDeadzone = function(number, threshold){
       percentage = (Math.abs(number) - threshold) / (1 - threshold);

       if(percentage < 0)
          percentage = 0;

       return percentage * (number > 0 ? 1 : -1);
    }



    function gamePadLoop() {
      setTimeout(gamePadLoop,100);

      if (state.controlMode != "gamepad") {
        return;
      }

      var gamepads = navigator.getGamepads();

      for (var i = 0; i < gamepads.length; ++i)
        {
          var pad = gamepads[i];
          // some pads are NULL I think.. some aren't.. use one that isn't null
          if (pad && pad.timestamp!=0)
          {

            var joystickX = applyDeadzone(pad.axes[2], 0.05);

            var joystickY = applyDeadzone(pad.axes[1], 0.15);

            state.tele.user.angle = joystickX;
            state.tele.user.throttle = limitedThrottle((joystickY * -1));

            if (state.tele.user.throttle == 0 && state.tele.user.throttle == 0) {
              state.brakeOn = true;
            } else {
              state.brakeOn = false;
            }

            if (state.tele.user.throttle != 0) {
              state.recording = true;
            } else {
              state.recording = false;
            }

            postDrive()

          }
            // todo; simple demo of displaying pad.axes and pad.buttons
        }
      }


    // Send control updates to the server every .1 seconds.
    function joystickLoop () {
       setTimeout(function () {
            postDrive()

          if (joystickLoopRunning && state.controlMode == "joystick") {
             joystickLoop();
          }
       }, 100)
    }

    // Control throttle and steering with device orientation
    function handleOrientation(event) {

      var alpha = event.alpha;
      var beta = event.beta;
      var gamma = event.gamma;

      if (beta == null || gamma == null) {
        deviceHasOrientation = false;
        state.controlMode = "joystick";
        console.log("Invalid device orientation values, switched to joystick mode.")
      } else {
        deviceHasOrientation = true;
        console.log("device has valid orientation values")
      }

      updateUI();

      if(state.controlMode != "tilt" || !deviceHasOrientation || state.brakeOn){
        return;
      }

      if(!initialGamma && gamma) {
        initialGamma = gamma;
      }

      var newThrottle = gammaToThrottle(gamma);
      var newAngle = betaToSteering(beta, gamma);

      // prevent unexpected switch between full forward and full reverse
      // when device is parallel to ground
      if (state.tele.user.throttle > 0.9 && newThrottle <= 0) {
        newThrottle = 1.0
      }

      if (state.tele.user.throttle < -0.9 && newThrottle >= 0) {
        newThrottle = -1.0
      }

      state.tele.user.throttle = limitedThrottle(newThrottle);
      state.tele.user.angle = newAngle;
    }

    function deviceOrientationLoop () {
       setTimeout(function () {
          if(!state.brakeOn){
            postDrive()
          }

          if (state.controlMode == "tilt") {
            deviceOrientationLoop();
          }
       }, 100)
    }

    var throttleUp = function(){
      state.tele.user.throttle = limitedThrottle(Math.min(state.tele.user.throttle + .05, 1));
      postDrive()
    };

    var throttleDown = function(){
      state.tele.user.throttle = limitedThrottle(Math.max(state.tele.user.throttle - .05, -1));
      postDrive()
    };

    var angleLeft = function(){
      state.tele.user.angle = Math.max(state.tele.user.angle - .1, -1)
      postDrive()
    };

    var angleRight = function(){
      state.tele.user.angle = Math.min(state.tele.user.angle + .1, 1)
      postDrive()
    };

    var updateDriveMode = function(mode){
      state.driveMode = mode;
      postDrive()
    };

    var toggleRecording = function(){
      state.recording = !state.recording
      postDrive()
    };

    var toggleBrake = function(){
      state.brakeOn = !state.brakeOn;
      initialGamma = null;


      if (state.brakeOn) {
        brake();
      }
    };

    var brake = function(i){
          console.log('post drive: ' + i)
          state.tele.user.angle = 0
          state.tele.user.throttle = 0
          state.recording = false
          state.driveMode = 'user';
          postDrive()


      i++
      if (i < 5) {
        setTimeout(function () {
          console.log('calling brake:' + i)
          brake(i);
        }, 500)
      };

      state.brakeOn = true;
      updateUI();
    };

    var limitedThrottle = function(newThrottle){
      var limitedThrottle = 0;

      if (newThrottle > 0) {
        limitedThrottle = Math.min(state.maxThrottle, newThrottle);
      }

      if (newThrottle < 0) {
        limitedThrottle = Math.max((state.maxThrottle * -1), newThrottle);
      }

      if (state.throttleMode == 'constant') {
        limitedThrottle = state.maxThrottle;
      }

      return limitedThrottle;
    }


    // var drawLine = function(angle, throttle) {
    //
    //   throttleConstant = 100
    //   throttle = throttle * throttleConstant
    //   angleSign = Math.sign(angle)
    //   angle = toRadians(Math.abs(angle*90))
    //
    //   var canvas = document.getElementById("angleView"),
    //   context = canvas.getContext('2d');
    //   context.clearRect(0, 0, canvas.width, canvas.height);
    //
    //   base={'x':canvas.width/2, 'y':canvas.height}
    //
    //   pointX = Math.sin(angle) * throttle * angleSign
    //   pointY = Math.cos(angle) * throttle
    //   xPoint = {'x': pointX + base.x, 'y': base.y - pointY}
    //
    //   context.beginPath();
    //   context.moveTo(base.x, base.y);
    //   context.lineTo(xPoint.x, xPoint.y);
    //   context.lineWidth = 5;
    //   context.strokeStyle = '#ff0000';
    //   context.stroke();
    //   context.closePath();
    //
    // };

    var betaToSteering = function(beta, gamma) {
      const deadZone = 5;
      var angle = 0.0;
      var outsideDeadZone = false;
      var controlDirection = (Math.sign(initialGamma) * -1)

      //max steering angle at device 35º tilt
      var fullLeft = -35.0;
      var fullRight = 35.0;

      //handle beta 90 to 180 discontinuous transition at gamma 90
      if (beta > 90) {
        beta = (beta - 180) * Math.sign(gamma * -1) * controlDirection
      } else if (beta < -90) {
        beta = (beta + 180) * Math.sign(gamma * -1) * controlDirection
      }

      // set the deadzone for neutral sterring
      if (Math.abs(beta) > 90) {
        outsideDeadZone = Math.abs(beta) < 180 - deadZone;
      }
      else {
        outsideDeadZone = Math.abs(beta) > deadZone;
      }

      if (outsideDeadZone && beta < -90.0) {
        angle = remap(beta, fullLeft, (-180.0 + deadZone), -1.0, 0.0);
      }
      else if (outsideDeadZone && beta > 90.0) {
        angle = remap(beta, (180.0 - deadZone), fullRight, 0.0, 1.0);
      }
      else if (outsideDeadZone && beta < 0.0) {
        angle = remap(beta, fullLeft, 0.0 - deadZone, -1.0, 0);
      }
      else if (outsideDeadZone && beta > 0.0) {
        angle = remap(beta, 0.0 + deadZone, fullRight, 0.0, 1.0);
      }

      // set full turn if abs(angle) > 1
      if (angle < -1) {
        angle = -1;
      } else if (angle > 1) {
        angle = 1;
      }

      return angle * controlDirection;
    };

    var gammaToThrottle = function(gamma) {
      var throttle = 0.0;
      var gamma180 = gamma + 90;
      var initialGamma180 = initialGamma + 90;
      var controlDirection = (Math.sign(initialGamma) * -1);

      // 10 degree deadzone around the initial position
      // 45 degrees of motion for forward and reverse
      var minForward = Math.min((initialGamma180 + (5 * controlDirection)), (initialGamma180 + (50 * controlDirection)));
      var maxForward = Math.max((initialGamma180 + (5 * controlDirection)), (initialGamma180 + (50 * controlDirection)));
      var minReverse = Math.min((initialGamma180 - (50 * controlDirection)), (initialGamma180 - (5 * controlDirection)));
      var maxReverse = Math.max((initialGamma180 - (50 * controlDirection)), (initialGamma180 - (5 * controlDirection)));

      //constrain control input ranges to 0..180 continuous range
      minForward = Math.max(minForward, 0);
      maxForward = Math.min(maxForward, 180);
      minReverse = Math.max(minReverse, 0);
      maxReverse = Math.min(maxReverse, 180);

      if(gamma180 > minForward && gamma180 < maxForward) {
        // gamma in forward range
        if (controlDirection == -1) {
          throttle = remap(gamma180, minForward, maxForward, 1.0, 0.0);
        } else {
          throttle = remap(gamma180, minForward, maxForward, 0.0, 1.0);
        }
      } else if (gamma180 > minReverse && gamma180 < maxReverse) {
        // gamma in reverse range
        if (controlDirection == -1) {
          throttle = remap(gamma180, minReverse, maxReverse, 0.0, -1.0);
        } else  {
          throttle = remap(gamma180, minReverse, maxReverse, -1.0, 0.0);
        }
      }

      return throttle;
    };

}();


function toRadians (angle) {
  return angle * (Math.PI / 180);
}

function remap( x, oMin, oMax, nMin, nMax ){
  //range check
  if (oMin == oMax){
      console.log("Warning: Zero input range");
      return None;
  };

  if (nMin == nMax){
      console.log("Warning: Zero output range");
      return None
  }

  //check reversed input range
  var reverseInput = false;
  oldMin = Math.min( oMin, oMax );
  oldMax = Math.max( oMin, oMax );
  if (oldMin != oMin){
      reverseInput = true;
  }

  //check reversed output range
  var reverseOutput = false;
  newMin = Math.min( nMin, nMax )
  newMax = Math.max( nMin, nMax )
  if (newMin != nMin){
      reverseOutput = true;
  };

  var portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
  if (reverseInput){
      portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin);
  };

  var result = portion + newMin
  if (reverseOutput){
      result = newMax - portion;
  }

return result;
}
