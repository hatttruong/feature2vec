<template>
  <v-layout row>
    <v-flex xs6 offset-xs3>
      <panel title="Register">
        <div slot="content">
          <form name="merge-tool-form" autocomplete="off">
            <v-text-field
              label="Email"
              v-model="email" >
            </v-text-field>
            <br>
            <v-text-field
              label="Password"
              type="password"
              v-model="password"
              autocomplete="new-password">
            </v-text-field>
          </form>
          <div class="error" v-html="error" />
          <br>
          <v-btn class="blue" dark @click="register">Register</v-btn>
        </div>
      </panel>
    </v-flex>
  </v-layout>
</template>

<script>
import AuthenticationService from '@/services/AuthenticationService'
import Panel from '@/components/Panel'

export default {
  name: 'Register',
  data () {
    return {
      email: '',
      password: '',
      error: null
    }
  },
  components: {
    Panel
  },
  methods: {
    async register () {
      try {
        const response = await AuthenticationService.register({
          email: this.email,
          password: this.password
        })
        console.log(response.data)
        this.$store.dispatch('setToken', response.data.token)
        this.$store.dispatch('setUser', response.data.user)
      } catch (e) {
        this.error = e.response.data.error
      }
    }
  }
}
</script>

<style scoped>

</style>
