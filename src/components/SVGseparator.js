const SVGseparator = ({ a, b, c, d, width }) => {

  return (

    <svg className='svg_separator' width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
      <polygon points={`0,${a} 33,${b} 66,${c} 100,${d} 100,${d+width} 66,${c+width} 33,${b+width} 0,${a+width}`} />
    </svg>


  )
}


SVGseparator.defaultProps = {
  a: 0,
  b: 0,
  c: 0,
  d: 0,
  width: 8
}

export default SVGseparator


// <svg className='svg_separator' width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
//   <polygon points={`0,100 33,${20+someNumber} 66,100 100,100 100,${70+someNumber} 66,80 33,10 0,80`} />
// </svg>

// const someNumber = Math.floor(Math.random() * 20);
