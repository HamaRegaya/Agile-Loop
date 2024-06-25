$(document).ready(function () {

    $('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        },
    });

    // Siri configuration
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
    });

    // Siri message animation
    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },
    });

    $("#MicBtn").click(function () { 
        //eel.playAssistantSound()


        // Call speech-to-text API
        $.ajax({
            url: "http://127.0.0.1:5000/speech_to_text",
            type: "POST",
            success: function(response) {
                // Populate the recognized text into the chatbox
                $("#chatbox").val(response.recognized_text);
                // Trigger PlayAssistant with the recognized text
                PlayAssistant(response.recognized_text);
                $("#Oval").attr("hidden", true);
                $("#SiriWave").attr("hidden", false);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    function doc_keyUp(e) {
        if (e.key === 'j' && e.metaKey) {
            eel.playAssistantSound()
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands()()
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    // to play assistant
    function PlayAssistant(message) {
        if (message != "") {
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);

            $.ajax({
                url: "http://127.0.0.1:5000/chat",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ message: message }),
                success: function(response) {
                    $("#responseContainer").text(response.response);

                    // Add a unique query parameter to the audio URL to prevent caching
                    var audio = new Audio(`http://127.0.0.1:5000/static/${response.audio_file}?timestamp=${new Date().getTime()}`);
                    audio.play();

                    // Event handler for when the audio ends
                    audio.onended = function() {
                        $("#Oval").attr("hidden", false);
                        $("#SiriWave").attr("hidden", true);
                    };
                },
                error: function(error) {
                    console.log(error);
                }
            });

            $("#chatbox").val("");
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
    }

    // toggle function to hide and display mic and send button 
    function ShowHideButton(message) {
        if (message.length == 0) {
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        } else {
            $("#MicBtn").attr('hidden', true);
            $("#SendBtn").attr('hidden', false);
        }
    }

    // key up event handler on text box
    $("#chatbox").keyup(function () {
        let message = $("#chatbox").val();
        ShowHideButton(message);
    });

    // send button event handler
    $("#SendBtn").click(function () {
        var userInput = $("#chatbox").val();
        PlayAssistant(userInput);
    });

    // enter press event handler on chat box
    $("#chatbox").keypress(function (e) {
        key = e.which;
        if (key == 13) {
            let message = $("#chatbox").val();
            PlayAssistant(message);
        }
    });

});

