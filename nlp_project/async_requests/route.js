const router = require('express').Router();
const async = require('async');
const request = require('request');

router.post('/:asyncMax', function (req, res, next) {
  var results = []
  req.body.forEach(_ => {
    results.push(null)
  });
  async.eachOfLimit(req.body, req.params.asyncMax, function(b, i, callback) {
    b.ngram = b.ngram.replace('\\','\\\\')
    b.ngram = b.ngram.replace('?','\\?')
    b.ngram = b.ngram.replace('*','\\*')
    b.ngram = b.ngram.replace('/','\\/')
    b.ngram = b.ngram.replace('~','\\~')
    b.ngram = encodeURIComponent(b.ngram)

    var query = {
      url: `https://api.phrasefinder.io/search?query=${b.ngram}&corpus=${b.corpus || 'spa'}&nmin=${b.nmin || 1}&nmax=${b.nmax || 5}&topk=${b.topk || 100}`,
      method: `GET`
    }

    _requestRetry(query, function(body) {
      results[i] = body
      callback()
    })
  }, function(err) {
    if (err) return next(err)
    res.send(results)
  })

});

function _requestRetry(query, cb) {
  request(query, function(err, result, body) {
    if (err) {
      console.log('error but retrying')
      _requestRetry(query, function(body) {
        console.log('success')
        cb(body)
      })
    } else {
      console.log(result.statusCode)
      if (result.statusCode != 200) {
        console.log(body)
      }
      cb(body)
    }
  })
}

module.exports = router;
