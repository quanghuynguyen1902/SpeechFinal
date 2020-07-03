<template>
  <el-container>
    <el-header>
      <img src="../../public/logo.png" class="logo" />
      <h1>Banking Assistant</h1>
    </el-header>
    <el-container>
      <el-aside>
        <img class="assistant" :src="assistant" />

        <el-button @click="changeAI()" type="success" icon="el-icon-refresh-left"></el-button>
      </el-aside>
      <el-main>
        <div v-if="answer != ''" class="speech-bubble">
          <p>{{ answer ? answer : "" }}</p>
          <el-button
            @click="textToSpeech(answer)"
            type="primary"
            v-if="answer !=''"
            icon="el-icon-video-play"
            round
          ></el-button>
        </div>
        <div v-if="loadAnswer">
          <ring-loader class="answering" :loading="true" :color="color" size="180px"></ring-loader>
        </div>
        <div v-if="recording">
          <img class="voice-effect" src="../../public/sound.gif" />
          <face-loader :loading="true" :color="color" size="150px"></face-loader>
        </div>
        <div>
          <el-button
            @click="startRecording()"
            type="primary"
            v-if="!recording"
            icon="el-icon-microphone"
            round
          >Record</el-button>

          <div v-if="recording">
            <el-button
              icon="el-icon-turn-off-microphone"
              type="danger"
              round
              @click="stopRecording()"
            >Record</el-button>
          </div>
        </div>
        <div>
          <div v-if="textResult !== ''" class="speech-bubble2">
            <p>{{ textResult ? textResult : "" }}</p>
          </div>
        </div>
      </el-main>
    </el-container>
    <el-footer>
      <el-row>
        <el-col :span="12">
          <p>Hotline: 19006969</p>
        </el-col>
        <el-col :span="12"></el-col>
      </el-row>
    </el-footer>
  </el-container>
</template>

<script>
import AIAssistant from "../../public/AI.png";
import redAIAssistant from "../../public/girl.gif";
import support from "../../public/support.gif";
import SiriWave from "siriwave";
import Recorder from "../../static/recorder";
import axios from "axios";
import RingLoader from "vue-spinner/src/RingLoader.vue";
import FaceLoader from "vue-spinner/src/ScaleLoader.vue";
import { Howl, Howler } from "howler";

var audio_context = new (window.AudioContext || window.webkitAudioContext)();
var recorder;

export default {
  name: "HelloWorld",
  props: {
    msg: String
  },

  data() {
    return {
      assistant: support,
      answer: "",
      loadAnswer: false,
      assistantArray: [AIAssistant, redAIAssistant, support],
      recording: false,
      selected: "vi-VN",
      textResult: "",
      apiKey: "your key",
      data: {
        audio: {
          content: null
        },
        config: {
          encoding: "LINEAR16",
          sampleRateHertz: 44100,
          languageCode: null
        }
      },
      loader: false,
      color: "#3AB982",
      size: "40px",
      result: false,
      resultError: false,
      textResult: "",
      headers: {
        voice: "female",
        speed: "",
        api_key: "your key"
      }
    };
  },

  methods: {
    startUserMedia(stream) {
      audio_context.resume();
      const input = audio_context.createMediaStreamSource(stream);
      // Media stream created
      recorder = new Recorder(input);
      // Recorder initialised
    },

    startRecording() {
      this.answer = "";
      this.textResult = "";
      audio_context.resume();
      this.recording = true;
      // Start Recording
      recorder && recorder.record();
      this.result = false;
      this.btn = false;
      this.btnStop = true;
    },
    stopRecording() {
      // Stopped Recording
      this.answer = "";
      recorder && recorder.stop();
      this.btnStop = false;
      this.loader = true;
      // create WAV download link using audio data blob
      this.processRecording();

      this.recording = false;
      recorder.clear();
    },
    processRecording: function() {
      const vm = this;

      recorder &&
        recorder.exportWAV(function(blob) {
          var reader = new window.FileReader();
          reader.readAsDataURL(blob);
          reader.onloadend = () => {
            const baseData = reader.result;
            const base64Data = baseData.replace("data:audio/wav;base64,", "");
            vm.data.audio.content = base64Data;
            vm.data.config.languageCode = vm.selected;
            axios
              .post(
                `https://speech.googleapis.com/v1/speech:recognize?key=${vm.apiKey}`,
                vm.data
              )
              .then(async response => {
                console.log(response);

                const result = response.data.results[0].alternatives[0];
                vm.textResult = result.transcript;
                vm.btn = true;
                vm.loader = false;
                vm.result = true;
                vm.getAnswer(vm.textResult)
                  .then(res => {
                    vm.answer = res;
                  })
                  .then(() => {
                    vm.textToSpeech(vm.answer);
                  });
              })
              .catch(error => {
                vm.loader = false;
                vm.resultError = true;
                if (error) vm.answer = " Mời quý khách thử lại";
                vm.textToSpeech(vm.answer);
                console.log("ERROR:" + error);
              });
          };
        });

      //
    },
    redirectError() {
      window.location.href = "http://localhost:8080/";
    },
    changeAI: function() {
      this.assistant = this.assistantArray[
        Math.floor(Math.random() * this.assistantArray.length)
      ];
    },

    textToSpeech: async function(answer) {
      console.log(answer);
      // await axios.post(`http://83e061c7c030.ngrok.io/text-to-speech`, {
      //   text: answer
      // });
      // let result = await axios.get(
      //   `http://83e061c7c030.ngrok.io/text-to-speech`
      // );
      // console.log(result);

      // var sound = new Howl({
      //   src: [JSON.parse(result.data).async],
      //   format: ["mp3"],
      //   autoplay: true,
      //   loop: false,
      //   volume: 0.5
      // });
      let result = await axios.post(`http://8c05b1de9dc9.ngrok.io/tts`, {
        text: answer
      });
      console.log(result);

      var sound = new Howl({
        src: [result.data.audio],
        format: ["mp3"],
        autoplay: true,
        loop: false,
        volume: 0.5
      });
      sound.once("load", function() {
        sound.play();
      });

      // Fires when the sound finishes playing.
      sound.on("end", function() {
        console.log("Finished!");
      });
    },
    getAudio: async function() {
      let res = await axios.post(
        `http://0e97573d5af5.ngrok.io:/home/tranhainam/speech/xxx_new/last_tacotron2/output.wav`
      );
    },
    getAnswer: async function(question) {
      this.loadAnswer = true;
      let result = await axios.post(`http://83e061c7c030.ngrok.io/answer`, {
        question: question
      });
      try {
        let res = await axios.get(`http://83e061c7c030.ngrok.io/answer`);
        this.loadAnswer = false;

        return res.data.answer[0];
      } catch (e) {
        this.answer =
          "Truy xuất câu trả lời không thành công. Xin vui lòng liên hệ nhân viên";
        this.loadAnswer = false;

        return this.answer;

        console.log(e);
      }
    }
  },
  created() {
    try {
      this.answer =
        "Chào mừng quý khách đến với trợ lý ảo của ngân hàng UET Bank!";

      window.AudioContext = window.AudioContext || window.webkitAudioContext;
      navigator.getUserMedia =
        navigator.getUserMedia || navigator.webkitGetUserMedia;
      window.URL = window.URL || window.webkitURL;

      audio_context = new AudioContext();
      console.log("Audio context set up.");
      console.log(
        "navigator.getUserMedia " +
          (navigator.getUserMedia ? "available." : "not present!")
      );
      // this.textToSpeech(this.answer);
    } catch (e) {
      alert("No web audio support in this browser!");
    }
    const that = this;
    navigator.getUserMedia(
      {
        audio: true
      },
      function(stream) {
        that.startUserMedia(stream);
      },
      function(e) {
        console.log("No live audio input: " + e);
      }
    );
    this.textToSpeech(this.answer);
  },
  components: {
    "ring-loader": RingLoader,
    "face-loader": FaceLoader
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.el-header {
  height: 120px !important;
  text-align: center;
  background: #1a7bbc;
  color: white;
  font-size: 30px;
}
.el-aside {
  width: 300px;
  height: auto;
}
.el-footer {
  height: auto !important ;
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100%;
  background: #1a7bbc;
  color: white;
  text-align: center;
  font-size: 30px;
}
.voice-effect {
  margin: 30px;
  border-radius: 100px;
  width: 200px;
  height: 200px;
}

.assistant {
  width: 300px;
}
.speech-bubble {
  position: relative;
  background: #00bda7;
  border-radius: 0.4em;
  height: auto;
  width: auto;
  word-wrap: break-word;
  padding: 60px 20px;
  margin: 1em 0;
  text-align: left;
  color: white;
  font-weight: bold;
  text-shadow: 0 -0.05em 0.1em rgba(0, 0, 0, 0.3);
}

.speech-bubble:after {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  width: 0;
  height: 0;
  border: 25px solid transparent;
  border-right-color: #00bda7;
  border-left: 0;
  border-bottom: 0;
  margin-top: -12.5px;
  margin-left: -25px;
}
.speech-bubble2 {
  position: relative;
  background: #c329e2;
  border-radius: 0.4em;
  height: auto;
  width: auto;
  word-wrap: break-word;
  padding: 60px 20px;
  margin: 1em 0;
  text-align: left;
  color: white;
  font-weight: bold;
  text-shadow: 0 -0.05em 0.1em rgba(0, 0, 0, 0.3);
}

.speech-bubble2:after {
  content: "";
  position: absolute;
  right: 0;
  top: 50%;
  width: 0;
  height: 0;
  border: 20px solid transparent;
  border-left-color: #c329e2;
  border-right: 0;
  border-bottom: 0;
  margin-top: -10px;
  margin-right: -20px;
}
.logo {
  width: 100px;
  height: 100px;
  float: left;
  padding-top: 10px;
}

.v-spinner .v-ring1 {
  margin: auto !important;
  padding-top: 30px !important;
  padding-bottom: 30px !important;
}
</style>
