import 'bootstrap/dist/css/bootstrap.min.css';
import React, {useEffect, useState} from "react";
import {api} from "./Config/app.config";
import AppNavbar from "./Components/Navbar";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import Home from "./Pages/Home";
import Login from "./Pages/Login";
import Verify from "./Pages/Verify";
import SignUp from "./Pages/SignUp";
import Logout from "./Pages/Logout";
import Admin from "./Pages/Admin";
import Profile from "./Pages/Profile";
import Workspace from "./Pages/Workspace";
import TestPage from "./Pages/TestPage";
import ProtectedRoute from "./Components/ProtectedRoute";
import Preload from "./Components/Preload";

export default function App() {

    const [user, setUser] = useState(null)
    const [userLoad, setUserLoad] = useState(true)


    useEffect(() => {
        handleRefresh();
    }, []);

    const handleRefresh = () => {
        setUserLoad(true)
        fetchUser()
    }

    const fetchUser = async () => {
        try {
            const response = await api.getMe();
            setUser(response);
        } catch (error) {
            setUser(null)
        }
        setUserLoad(false)
    };

        return (
            <>
                {userLoad? <Preload/> :
                    <BrowserRouter basename={"/wiki/demo"}>
                        <AppNavbar user={user}/>
                        <Routes>
                            <Route path={"/"} element={<Home user={user}/>}/>
                            <Route path={"/login"} element={<Login/>}/>
                            <Route path={"/verify"} element={<Verify onRefresh={handleRefresh}/>}/>
                            {/*<Route path={"/signup"} element={<SignUp/>}/>*/}
                            <Route path={"/logout"} element={<Logout onRefresh={handleRefresh}/>}/>
                            <Route element={<ProtectedRoute requirement={
                                user !== null && user.wiki_api_client !== null && user.wiki_api_client.responsibility === 'ADMIN'
                            }/>}>
                                <Route path={"/admin"} element={<Admin/>}/>
                            </Route>
                            <Route element={<ProtectedRoute requirement={
                                user !== null && user.wiki_api_client !== null
                            }/>}>
                                <Route path={"/profile"} element={<Profile/>}/>
                                <Route path={"/workspace/*"} element={<Workspace/>}/>
                            </Route>
                            <Route path={"/test/*"} element={<TestPage/>}/>
                        </Routes>
                    </BrowserRouter>}
            </>
            /*<UserContext.Provider value={user}>*/

           /* </UserContext.Provider>*/
        )
}
