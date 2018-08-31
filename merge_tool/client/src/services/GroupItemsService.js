import Api from '@/services/Api'

export default {
  index () {
    return Api().get('groupitems')
  },
  create () {
    return Api().post('creategroup')
  }
}
