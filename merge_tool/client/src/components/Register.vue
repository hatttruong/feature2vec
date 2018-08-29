<template>
  <div>
    <h1>Register</h1>

    <input type="email" name="email" v-model="email" placeholder="email"/>
    <br>
    <button @click="register">Register</button>
  </div>

</template>

<script>
import AuthenticationService from '@/services/AuthenticationService'

export default {
  name: 'Register',
  data () {
    return {
      email: ''
    }
  },
  methods: {
    async register () {
      const response = await AuthenticationService.register({
        email: this.email
      })

      console.log(response.data)
    }
  }
}
</script>

<style scoped>

</style>
