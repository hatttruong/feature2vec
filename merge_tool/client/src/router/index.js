import Vue from 'vue'
import Router from 'vue-router'
import Register from '@/components/Register'
import Login from '@/components/Login'
import Items from '@/components/Items'
import Concepts from '@/components/Concepts'
import MergeItems from '@/components/MergeItems'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/merge',
      name: 'merge',
      component: MergeItems
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/items',
      name: 'items',
      component: Items
    },
    {
      path: '/concepts',
      name: 'concepts',
      component: Concepts
    },
    {
      path: '*',
      redirect: 'merge'
    }
  ]
})
