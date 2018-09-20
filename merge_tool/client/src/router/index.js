import Vue from 'vue'
import Router from 'vue-router'
import Register from '@/components/Register'
import Login from '@/components/Login'
import Dashboard from '@/components/Dashboard'
import Items from '@/components/Items'
import Concepts from '@/components/Concepts'
import ConceptDetail from '@/components/ConceptDetail'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard
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
      path: '/concepts/:conceptid',
      name: 'concept',
      component: ConceptDetail
    },
    {
      path: '*',
      redirect: 'dashboard'
    }
  ]
})
