const DataOutputList = ({ dataArr }) => {

  return (
    <ul className='data_output_list'>
    {dataArr.map((date, index) => (
      <li key={date.id}>
      <span>{date.name}</span>
      <span>{date.value}{date.scale}</span>
      <p className='help_message'>{date.help}</p>
      </li>
    ))}
    </ul>
  )
}


export default DataOutputList
