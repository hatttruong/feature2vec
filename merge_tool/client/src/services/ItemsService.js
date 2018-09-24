import Api from '@/services/Api'

export default {
  index () {
    return Api().get('items')
  },
  show (itemid) {
    return Api().get(`items/${itemid}`)
  }
}
