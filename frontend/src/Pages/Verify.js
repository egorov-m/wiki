import React, { useState } from "react";
import {Button, Form} from "react-bootstrap";
import "../Styles/Login.css"
import {api} from "../Config/app.config";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import {useNavigate} from "react-router-dom";


export default function Verify({onRefresh}){

    const [code, setCode] = useState();
    const [isError, setIsError] = useState(false);
    const [errorText, setErrorText] = useState("")
    let navigation = useNavigate()

    async function handleFormSubmit(event) {
        event.preventDefault();
        try {
            await api.verify(code);
            onRefresh()
            navigation(`/`)
            }
            catch (error){
                setErrorText(error.response.data.message)
                setIsError(true)
            }
    }

    return(
        <div className="login-form">
            <Form onSubmit={handleFormSubmit}>
                <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
                    <Form.Label>Код подтверждения</Form.Label>
                    <Form.Control
                        placeholder="123456"
                        value={code}
                        onChange={(event) => setCode(event.target.value)}
                    />
                </Form.Group>
                {isError && (
                    <p style={{ color: 'red', fontFamily: 'Inter', fontSize: '11px' }}>
                        <ErrorOutlineIcon sx={{ height: '20px' }} /> {errorText}
                    </p>
                )}
                <Button id="accent-button" type="submit" variant="outline-primary"> Подтвердить </Button>
            </Form>
        </div>
    )
}