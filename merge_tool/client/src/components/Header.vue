<template>
    <v-toolbar fixed class="blue" dark>
      <v-toolbar-title class="mr-4">
        <span class="home"
          @click="navigateTo({name: 'dashboard'})">
          MergeTool
        </span>
      </v-toolbar-title>

      <v-toolbar-items>
        <v-btn
          flat dark
          @click="navigateTo({name: 'concepts'})">
          Concepts
        </v-btn>
        <v-btn
          flat dark
          @click="navigateTo({name: 'items'})">
          Items
        </v-btn>
      </v-toolbar-items>

      <v-spacer></v-spacer>

      <v-toolbar-items>
        <v-btn
          v-if="!$store.state.isUserLoggedIn"
          flat dark
          @click="navigateTo({name: 'login'})">
          Login
        </v-btn>
        <v-btn
          v-if="!$store.state.isUserLoggedIn"
          flat dark
          @click="navigateTo({name: 'register'})">
          Sign Up
        </v-btn>
        <v-btn
          v-if="$store.state.isUserLoggedIn"
          flat dark
          @click="logout()">
          Log Out
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
</template>

<script>
export default {
  name: 'Header',

  methods: {
    navigateTo (route) {
      this.$router.push(route)
    },
    logout () {
      this.$store.dispatch('setToken', null)
      this.$store.dispatch('setUser', null)
      this.$router.push({
        name: 'merge'
      })
    }
  }
}
</script>

<style scoped>
.home {
  cursor: pointer;
}

.home:hover {
  color: blue;
}
</style>
