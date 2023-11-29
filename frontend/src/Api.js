import {instance} from "./Config/api.config";

export default class Api {
    async login(email) {
        await instance.post(`/auth/login`,
            {
                "email": email
            }).then((response) => {
            localStorage.setItem('verify', response.data.verify_token)
        })
    }

    async signup(email, username, first_name, last_name, second_name, position, organization_id, is_user_agreement_accepted) {
        await instance.post(`/auth/signup`,
            {
                "email": email,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "second_name": second_name,
                "position": position,
                "is_user_agreement_accepted": is_user_agreement_accepted,
                "organization_id": organization_id
            }).then((response) => {
            localStorage.setItem('verify', response.data.verify_token)
        })
    }

    async verify(code) {
        await instance.get(`/auth/verify?token=${localStorage.getItem("verify")}&verification_code=${code}`)
            .then((resp) => {
                localStorage.setItem("token", resp.data.msg);
            })
    }

    async logout() {
        localStorage.setItem('token', "");
    }

     async getUsers() {
         let users = []
         await instance.get(`/user/all`,)
             .then((resp) => {
                 resp.data.items.forEach((user) => {
                         users.push(user)
                     }
                 )
             })
         return users;
    }


     async getOrganizations() {
         let organizations = []
         await instance.get(`/organization/all`,)
             .then((resp) => {
                 resp.data.items.forEach((organization) => {
                         organizations.push(organization)
                 })
             })
         return organizations
     }

    async addOrganizations(name, description, access){
        await instance.post(`/organization/`,
            {
                "name": name,
                "description": description,
                "access": access
            })
    }

     async getMe() {
        let user = null
          await instance.get(`/user/me`).then((resp) => {
              user = resp.data
         })
        return user
    }

    async approveUser(username, responsibility, description){
        await instance.post(`/admins/approve_user?username=${username}`, {
            "responsibility": responsibility,
            "api_client_description": description
        } )
    }

    async createApprovedUser(email, username, firstName, lastName, secondName,position, responsibility){
        await instance.post(`/user/verified`, {
            "email": email,
            "first_name": firstName,
            "is_enabled": true,
            "is_user_agreement_accepted": true,
            "is_verified_email": true,
            "last_name": lastName,
            "position": position,
            "second_name": secondName,
            "username": username,
            "wiki_api_client": {
                "description": "",
                "is_enabled": true,
                "responsibility": responsibility
            }
        } )
    }

    async getWorkspaces(){
        let workspaces = []
        await instance.get(`/workspace/all`).then((resp)=>{
            resp.data.forEach((workspace) => {
                workspaces.push(workspace)
            })}
        )
       return workspaces
    }

    async addWorkspace(title){
        await instance.post(`/workspace`,{
            "title" : title
        })
    }

    async getWorkspaceInfo(id){
        let workspace = null
        await instance.get(`/workspace/info?workspace_id=${id}`).then((resp)=>{
            workspace=resp.data
           }
        )
        return workspace
    }

    async addDocument(title, workspace_id, parent_document_id){
        await instance.post(`/document`,{
            "title" : title,
            "workspace_id": workspace_id,
            "parent_document_id": parent_document_id
        })
    }

    async getDocumentsTree(workspace_id){
        let documents = []
        await instance.get(`/document/tree?workspace_id=${workspace_id}`).then((resp)=>{
            resp.data.forEach((document) => {
                documents.push(document)
            })}
        )
        return documents
    }

    async getDocumentsInfo(document_id){
        let document = null
        await instance.get(`/document/info?workspace_id=${document_id}`).then((resp)=> {
            document = resp.data
        })
        return document
    }

    async saveDocument(document_id){
        await instance.post(`/document/${document_id}/save`)
    }

    async publishDocument(document_id){
        await instance.post(`/document/${document_id}/publish`)
    }


    async addBlock(document_id, position, type_block){
        await instance.post(`/blocks`,{
            "document_id": document_id,
            "position": position,
            "type_block": type_block
        })
    }

    async deleteBlock(block_id){
        await instance.delete(`/blocks?block_id=${block_id}`)
    }

    async updateBlockData(block_id, content){
        await instance.put(`/blocks/data`,{
            "block_id": block_id,
            "content": content
        })
    }

    async getBlocks(document_id){
        let res = []
        await instance.get(`/blocks/data?document_id=${document_id}`).then((resp)=>{
            resp.data.forEach((item) => {
                res.push(item)
            })}
        )
        return res
    }
}