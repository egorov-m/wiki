import {api} from "../Config/app.config";
import React from "react";
import {Modal, Button} from "react-bootstrap";
import {useNavigate} from "react-router-dom";


export default function Logout({onRefresh}) {

    let navigation = useNavigate()
    React.useEffect( () => {
        async function fetch(){
            await api.logout()
            onRefresh()
            navigation(`/`)
        }
        fetch()
    })
    return (
        <div
        className="modal show"
        style={{ display: 'block', position: 'initial' }}>
        <Modal.Dialog>
            <Modal.Header>
                <Modal.Title>Successful</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <p>You have successfully logged out of your account.</p>
            </Modal.Body>
            <Modal.Footer>
                <Button onClick={()=> window.location.href = "#"} variant="primary">Go back</Button>
            </Modal.Footer>
        </Modal.Dialog>
    </div>)
}