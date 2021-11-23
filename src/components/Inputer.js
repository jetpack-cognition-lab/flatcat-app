// import React, { useState } from "react"
import React from "react"

const Inputer = ({ Value, setFcuiName }) => {
    // const [input, setInput] = useState(Value)

  return (
    <form>
      <div className='inputer_group'>
        <input
        type='text'
        value={Value}
        onChange={(e) => setFcuiName(e.target.value)} />
      </div>
    </form>
  )
}

export default Inputer
