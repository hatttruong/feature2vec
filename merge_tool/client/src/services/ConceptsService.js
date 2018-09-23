import Api from '@/services/Api'

export default {
  index () {
    return Api().get('concepts')
  },
  show (conceptid) {
    return Api().get(`concepts/${conceptid}`)
  },
  post (concept) {
    return Api().post('create-concept', concept)
  },
  put (concept) {
    return Api().put(`concepts/${concept.conceptid}`, concept)
  }
}
