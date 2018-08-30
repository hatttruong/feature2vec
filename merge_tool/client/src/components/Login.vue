<template>
  <v-layout row>
    <v-flex xs6 offset-xs3>
      <div class="white elevation-2">
        <v-toolbar flat dense class="blue" dark>
          <v-toolbar-title>Login</v-toolbar-title>
        </v-toolbar>
        <div class="pl-4 pr-4 pt-2 pb-2">
          <br>
          <v-text-field
            label="Email"
            v-model="email" >
          </v-text-field>
          <br>
          <v-text-field
            label="Password"
            type="password"
            v-model="password" >
          </v-text-field>
          <div class="error" v-html="error" />
          <br>
          <v-btn class="blue" dark @click="login">
            Login
          </v-btn>
        </div>
      </div>
    </v-flex>
  </v-layout>
</template>

<script>
import AuthenticationService from '@/services/AuthenticationService'

export default {
  name: 'Login',
  data () {
    return {
      email: '',
      password: '',
      error: null
    }
  },
  methods: {
    async login () {
      try {
        const response = await AuthenticationService.login({
          email: this.email,
          password: this.password
        })
        console.log(response.data)
      } catch (e) {
        this.error = e.response.data.error
      }
    }
  }
}
</script>

<style scoped>

</style>
