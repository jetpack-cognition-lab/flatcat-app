// import React, { useState } from "react"
import React from "react"

const Inputer = ({ Value, setFcuiName, confNameHandleSubmit }) => {
    // const [input, setInput] = useState(Value)
  return (
    <form onSubmit={confNameHandleSubmit}>
      <div className='inputer_group'>
        <input
        type='text'
        value={Value}
      onChange={(e) => setFcuiName(e.target.value)} />

	  <input type="submit" value="Set" />

      </div>
    </form>
  )
}

export default Inputer
