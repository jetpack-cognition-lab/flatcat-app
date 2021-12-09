import React from "react";
import io from 'socket.io-client';

class Dashboard extends React.Component {
    state = {
        socketData: "",
        socketStatus:"On"
    }
    componentWillUnmount() {
        this.socket.close()
        console.log("socketDashboard component unmounted")
    }
    componentDidMount() {
        var sensorEndpoint = "http://localhost:5000"
        this.socket = io.connect(sensorEndpoint, {
            reconnection: true,
	    // transports: ['polling', 'websocket']
        });
        console.log("socketDashboard component mounted", this.socket)
        this.socket.on("responseMessage", message => {
            this.setState({'socketData': message.temperature})

            // console.log("socketDashboard responseMessage", message)
        })
            
    }
    handleEmit=()=>{
        if(this.state.socketStatus==="On"){
            this.socket.emit("message", {'data':'Stop Sending', 'status':'Off'})
            this.setState({'socketStatus':"Off"})
	}
	else{
            this.socket.emit("message", {'data':'Start Sending', 'status':'On'})
            this.setState({'socketStatus':"On"})
        }
        console.log("socketDashboard Emit Clicked")
    }
    render() {
        return (
            <React.Fragment>
            <div>Data: {this.state.socketData}</div>
            <div>Status: {this.state.socketStatus}</div>
            <div onClick={this.handleEmit}> Start/Stop</div>
            </React.Fragment>
        )
    }
}
export default Dashboard;
