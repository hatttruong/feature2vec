import Api from '@/services/Api'

export default {
  index () {
    return Api().get('concepts')
  },
  getConcepts (createdBy, limit) {
    return Api().get('concepts', {
      params: {
        createdBy: createdBy,
        limit: limit
      }
    })
  },
  create () {
    return Api().post('createconcept')
  }
}
