import falcon
import json
import narou_scraiping as api

class SearchRecommend:
    def on_post(self, req, resp):
        print('tre')
        req_data = json.loads(req.bounded_stream.read())
        print(req_data['novel_url'])
        print('hreee')
        recommend = api.get_recommend_novel(req_data['novel_url'])

        resp.body = json.dumps(recommend, ensure_ascii=False)

app = falcon.API()
app.add_route('/sample', SearchRecommend())

if __name__ == "__main__":
    from wsgiref import simple_server

    httpd = simple_server.make_server("127.0.0.1", 8080, app)
    httpd.serve_forever()