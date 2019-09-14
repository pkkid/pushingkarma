<template>
  <Modal v-if='display' @close='display=false' :width='"800px"' :padding='"0px"' :escClose=true>
    <div slot='body'>
      <div id='login'>
        <div class='bgimg'></div>
        <div class='loginform'>
          <h3>Login to PushingKarma <span>Amazing things await you</span></h3>
          <img class='google' src='@/assets/img/google_signin.png'/>
          <form>
            <label for='username'>Username</label>
            <input type='text' id='username' name='username' spellcheck='false' autocomplete='off' autofocus='true'/>
            <label for='password'>Password</label>
            <input type='password' id='password' name='password' autocomplete='off'/>
            <button type='submit'>Login</button>
          </form>
          <div class='footnote'>
            © 2019 PushingKarma. All Rights Reserved.<br/>
            Sunrise graphic by <a href='https://dribbble.com/shots/3200530-Sunrise-wallpaper'>Louis Coyle</a>.
          </div>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script>
  import Modal from '@/components/utils/Modal';

  export default {
    name: 'Navigation',
    components: {Modal},
    data: () => ({
      display: false
    }),
  };
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  #login {
    .bgimg {
      background-image: url('../assets/img/louiscoyle.png');
      background-size: 550px;
      float: right;
      width: 450px;
      height: 500px;
      background-position: 0px -28px;
      border-top-right-radius: 8px;
      border-bottom-right-radius: 8px;
      box-shadow: inset 0 0 100px rgba(0,0,0,0.5);
      position: relative;
      left: 2px;
    }
    
    .loginform {
      padding: 20px 30px;
      height: 500px;
      width: 350px;
      color: $dark-bg0;

      h3 {
        font-size: 20px;
      }
      h3 span {
        font-size: 13px;
        display: block;
        padding: 3px 0px;
        font-weight: 100;
      }
      .google {
        display: block;
        cursor: pointer;
        position: relative;
        right: 2px;
        margin: 20px 0px;
      }
      label {
        font-size: 13px;
        display: block;
        padding: 3px 0px;
        font-weight: 100;
        margin-top: 10px;
      }
      input {
        width: 100%;
        border-radius: 6px;
        border: 2px solid #ddd;
        background-color: #f8f8f8;
        padding: 10px;
      }
      button {
        background-color: $light-blue1;
        color: $light-bgh;
        width: 100%;
        padding: 12px;
        border-radius: 6px;
        border-width: 0px;
        cursor: pointer;
        margin-top: 30px;
      }
      .footnote {
        position: absolute;
        bottom: 20px;
        text-align: center;
        color: #888;
        font-size: 12px;
        margin-top: 30px;
        width: 290px;
        line-height: 16px;
      }
    }
  }
</style>
