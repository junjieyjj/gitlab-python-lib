import requests, json, base64


class git_operation(object):
    def __init__(self,domain,token):
        self.domain = domain
        self.token = token

    def create_or_update_webhook(self, git_project_id, hook_url, **kwargs):
        params_str = ''
        if kwargs:
            for k,v in kwargs.items():
                params_str = params_str + '&%s=%s' % (k, v)
        create_webhook_url = '%s/api/v4/projects/%s/hooks?private_token=%s&url=%s%s' % (self.domain, git_project_id, self.token, hook_url, params_str)
        exist_webhook_list = self.list_webhook(git_project_id)
        if exist_webhook_list:
            for webhook in json.loads(exist_webhook_list.decode("utf-8")):
                # print(webhook)
                if webhook["url"] == hook_url:
                    hook_id = webhook["id"]
                    update_webhook_url = '%s/api/v4/projects/%s/hooks/%s?private_token=%s%s' % (self.domain, git_project_id, hook_id, self.token, params_str)
                    rsp = requests.put(update_webhook_url, verify=False)
                    if rsp.status_code == 404:
                        return False
                    else:
                        return True
        rsp = requests.post(create_webhook_url, verify=False)
        # print(rsp.content)
        if rsp.status_code == 404:
            return False
        else:
            return True

    def list_webhook(self, git_project_id):
        list_webhook_url = '%s/api/v4/projects/%s/hooks?private_token=%s' % (self.domain, git_project_id, self.token)
        rsp = requests.get(list_webhook_url, verify=False)
        return rsp.content

    def branch_exist(self, git_project_id, branch):
        branch_exist_url = '%s/api/v4/projects/%s/repository/branches/%s?private_token=%s' % (self.domain, git_project_id, branch, self.token)
        rsp = requests.get(branch_exist_url, verify=False)
        if rsp.status_code == 404:
            return False
        else:
            return True

    def get_project_id(self, git_project_name):
        list_projects_url = '%s/api/v4/projects?private_token=%s&search=%s&simple=true' % (self.domain, self.token, git_project_name)
        rsp = requests.get(list_projects_url, verify=False)
        obj = json.loads(rsp.content.decode('utf-8'))
        for i in obj:
            if i["name"] == git_project_name:
                return i["id"]

    def create_git_branch(self, git_project_id, branch):
        print("create branch:" + branch)
        create_git_branch_url = '%s/api/v4/projects/%s/repository/branches?private_token=%s&branch=%s' \
                                '&ref=master' \
                                % (self.domain, git_project_id, self.token, branch)
        requests.post(create_git_branch_url, verify=False)

    def delete_git_branch(self, git_project_id, branch):
        print("delete branch:" + branch)
        delete_git_branch_url = '%s/api/v4/projects/%s/repository/branches/%s?private_token=%s' \
                                % (self.domain, git_project_id, branch, self.token)
        res = requests.delete(delete_git_branch_url, verify=False)
        print( res.text)

    def create_or_update_file(self,git_project_id, branch, file_path, file_content, commit_message):
        print("create/update file:" + file_path)
        create_file_url = '%s/api/v4/projects/%s/repository/files/%s?private_token=%s&content=%s&branch=%s' \
                          '&commit_message=%s' \
                          % (self.domain, git_project_id, file_path.replace('/', '%2F'), self.token,
                             file_content, branch, commit_message)

        update_file_res = requests.post(create_file_url, verify=False)
        if "A file with this name already exists" in update_file_res.text:
            update_file_res = requests.put(create_file_url, verify=False)
        print(update_file_res.text)

    def create_or_update_fileV2(self, git_project_id, branch, file_path, file_content, commit_message):
        print("create/update file:" + file_path)
        create_file_url = '%s/api/v4/projects/%s/repository/files/%s?private_token=%s' \
                          % (self.domain, git_project_id, file_path.replace('/', '%2F'), self.token)
        data = {'branch': branch, 'content': file_content, 'commit_message': commit_message}
        update_file_res = requests.post(create_file_url, data=data, verify=False)
        if "A file with this name already exists" in update_file_res.text:
            update_file_res = requests.put(create_file_url, data=data, verify=False)
        print(update_file_res.text)

    def create_and_approve_merge_request(self, git_project_id, issue_key, branch):
        print("merge branch:" + branch)
        # create merge request
        merge_request_url = '%s/api/v4/projects/%s/merge_requests?private_token=%s&source_branch=%s&target_branch' \
                            '=master&title=%s&description=%s' \
                            % (self.domain, git_project_id, self.token, branch, issue_key, issue_key)

        merge_request_res = requests.post(merge_request_url, verify=False)
        merge_request_info = self.analyze_unicode(merge_request_res.text)

        # approve merge request
        approve_merge_request_url = '%s/api/v4/projects/%s/merge_requests/%s/merge?private_token=%s' \
                                    % (self.domain, git_project_id, merge_request_info['iid'], self.token)
        approve_merge_request_res = requests.put(approve_merge_request_url, verify=False)

    def get_file_content(self, git_project_id, file_path, branch):
        try:
            get_file_url = '%s/api/v4/projects/%s/repository/files/%s?private_token=%s&ref=%s' \
                           % (self.domain, git_project_id, file_path.replace('/', '%2F'), self.token, branch)
            get_file_res = requests.get(get_file_url, verify=False)
            print(get_file_res)
            file_info = self.analyze_unicode(get_file_res.text)
            file_content = base64.b64decode(file_info['content'])
            return file_content
        except Exception as e:
            print(e)
            return None

    def upload_file(self, git_porject_id, file_path):
        files = {'file': open(file_path, 'rb')}
        upload_file_url = '%s/api/v4/projects/%s/uploads?private_token=%s' \
                          % (self.domain, git_porject_id, self.token)
        upload_file_res = requests.post(upload_file_url, files=files, verify=False)
        return upload_file_res

    def analyze_unicode(self, text):
        json_str = json.dumps(text)
        json_result = json.loads(json_str).encode('utf-8')
        json_result = json.loads(json_result)
        return json_result
