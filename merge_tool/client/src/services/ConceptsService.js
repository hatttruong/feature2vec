import Api from '@/services/Api'

export default {
  index () {
    return Api().get('concepts')
  },
  create () {
    return Api().post('createconcept')
  }
}
